from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.utils import timezone

from api.cmc.services import fetch_and_save_full
from api.models import CryptoPrice, CryptoAsset
from api.ai.gemini_client import call_gemini, GeminiError
from api.ai.openai_client import call_openai, OpenAIError
from users.models import UserCryptoAsset


def _is_fresh(point: CryptoPrice, max_age_minutes: int) -> bool:
    max_age = timezone.now() - timedelta(minutes=max_age_minutes)
    return point.timestamp >= max_age


def _get_latest_point(symbol: str) -> Optional[CryptoPrice]:
    try:
        asset = CryptoAsset.objects.get(symbol=symbol.upper())
    except CryptoAsset.DoesNotExist:
        return None
    return CryptoPrice.objects.filter(asset=asset).order_by("-timestamp").first()


def get_or_fetch_snapshot(symbol: str, max_age_minutes: int = 10) -> Tuple[CryptoPrice, bool]:
    latest = _get_latest_point(symbol)
    if latest and _is_fresh(latest, max_age_minutes):
        return latest, False

    price_obj = fetch_and_save_full(symbol)
    return price_obj, True


def _fmt(val) -> str:
    return "null" if val is None else str(val)


def _build_single_prompt(symbol: str, snapshot: CryptoPrice, lang: str) -> str:
    lang = (lang or "uk").lower()
    if lang not in ("uk", "en"):
        lang = "en"

    ts = snapshot.timestamp.isoformat()
    meta = f"symbol: {snapshot.asset.symbol}\nts: {ts}\nprice: {snapshot.price}\n"
    ohlc = (
        f"ohlc (latest): open { _fmt(snapshot.open_price)}, high { _fmt(snapshot.high_price)}, "
        f"low { _fmt(snapshot.low_price)}, close { _fmt(snapshot.close_price)}\n"
    )
    pct = (
        f"percent changes: 1h {_fmt(snapshot.percent_change_1h)}, 24h {_fmt(snapshot.percent_change_24h)}, "
        f"7d {_fmt(snapshot.percent_change_7d)}, 30d {_fmt(snapshot.percent_change_30d)}, "
        f"60d {_fmt(snapshot.percent_change_60d)}, 90d {_fmt(snapshot.percent_change_90d)}\n"
    )
    caps = (
        f"market_cap: {_fmt(snapshot.market_cap)}, dominance: {_fmt(snapshot.market_dominance)}, "
        f"volume_24h: {_fmt(snapshot.volume_24h)}\n"
    )
    supply = (
        f"supply: circulating {_fmt(snapshot.circulating_supply)}, total {_fmt(snapshot.total_supply)}, "
        f"max {_fmt(snapshot.max_supply)}\n"
    )

    if lang == "uk":
        instructions = (
            "Ти аналітик крипти. Мова: uk.\n"
            "Дисклеймер: це не фінансова порада. Не гарантуй результат.\n"
            "Зроби стислий огляд (5-7 булетів, до 700 символів):\n"
            "- поточний стан і помітні рухи (%, обсяг)\n"
            "- головні ризики/невизначеності\n"
            "- твоя думка: «ймовірно зростатиме/падатиме» з обережним орієнтиром ціни (не гарантія)\n"
            "- заверши явним дисклеймером, що це не фінансова порада\n"
            "Використовуй лише надані дані.\n"
        )
    else:
        instructions = (
            "You are a crypto analyst. Language: en.\n"
            "Disclaimer: this is not financial advice. Do not guarantee outcomes.\n"
            "Provide a concise view (5-7 bullets, under 700 characters):\n"
            "- current state and notable moves (%, volume)\n"
            "- key risks/uncertainties\n"
            "- your view: likely to rise/fall with a cautious price waypoint (not guaranteed)\n"
            "- end with an explicit disclaimer: not financial advice\n"
            "Use only the supplied data.\n"
        )

    return instructions + "\nData (latest):\n" + meta + ohlc + pct + caps + supply


def analyze_symbol(symbol: str, lang: str = "uk") -> Dict:
    symbol_clean = symbol.upper().strip()
    if not symbol_clean:
        raise ValueError("Symbol is required")

    price_obj, fetched_now = get_or_fetch_snapshot(symbol_clean)
    prompt = _build_single_prompt(symbol_clean, price_obj, lang)

    analysis_text = call_gemini(prompt)
    age_sec = (timezone.now() - price_obj.timestamp).total_seconds()

    return {
        "symbol": symbol_clean,
        "timestamp": price_obj.timestamp.isoformat(),
        "data_age_seconds": int(age_sec),
        "fetched_now": fetched_now,
        "analysis": analysis_text,
    }


def analyze_symbol_openai(symbol: str, lang: str = "uk") -> Dict:
    symbol_clean = symbol.upper().strip()
    if not symbol_clean:
        raise ValueError("Symbol is required")

    price_obj, fetched_now = get_or_fetch_snapshot(symbol_clean)
    prompt = _build_single_prompt(symbol_clean, price_obj, lang)

    analysis_text = call_openai(prompt)
    age_sec = (timezone.now() - price_obj.timestamp).total_seconds()

    return {
        "symbol": symbol_clean,
        "timestamp": price_obj.timestamp.isoformat(),
        "data_age_seconds": int(age_sec),
        "fetched_now": fetched_now,
        "analysis": analysis_text,
    }


def _snapshot_for_portfolio(asset: UserCryptoAsset, max_age_minutes: int) -> Tuple[Optional[CryptoPrice], bool]:
    latest = _get_latest_point(asset.crypto.symbol)
    if latest and _is_fresh(latest, max_age_minutes):
        return latest, False
    try:
        refreshed = fetch_and_save_full(asset.crypto.symbol)
        return refreshed, True
    except Exception:
        return latest, False


def _build_portfolio_prompt(snapshots: List[Dict], lang: str) -> str:
    lang = (lang or "uk").lower()
    if lang not in ("uk", "en"):
        lang = "en"

    lines = []
    for item in snapshots:
        lines.append(
            f"{item['symbol']}: amount={item['amount']}, price={item['price']}, "
            f"value={item['value']}, weight_pct={item['weight_pct']}, "
            f"vol_24h={_fmt(item['volume_24h'])}, cap={_fmt(item['market_cap'])}, "
            f"%1h={_fmt(item['percent_change_1h'])}, %24h={_fmt(item['percent_change_24h'])}, "
            f"%7d={_fmt(item['percent_change_7d'])}"
        )
    joined = "\n".join(lines)

    if lang == "uk":
        instructions = (
            "Ти аналітик портфеля. Мова: uk.\n"
            "Дисклеймер: це не фінансова порада. Не гарантуй результати.\n"
            "Зроби стислий огляд (6-8 булетів, до 900 символів):\n"
            "- структура портфеля та концентрація\n"
            "- ризики/волатильність, на що звернути увагу\n"
            "- твоя думка: які позиції можуть зростати/падати, з обережними орієнтирами (не гарантія)\n"
            "- рекомендації з ризик-менеджменту без конкретних інструкцій щодо купівлі/продажу\n"
            "- заверши явним дисклеймером\n"
        )
    else:
        instructions = (
            "You are a portfolio analyst. Language: en.\n"
            "Disclaimer: this is not financial advice. Do not guarantee outcomes.\n"
            "Give a concise view (6-8 bullets, under 900 characters):\n"
            "- portfolio structure and concentration\n"
            "- risks/volatility to watch\n"
            "- your view: which positions may rise/fall with cautious waypoints (not guaranteed)\n"
            "- risk management suggestions without explicit buy/sell calls\n"
            "- end with an explicit disclaimer\n"
        )

    return instructions + "\nPortfolio snapshot:\n" + joined


def analyze_portfolio(user, lang: str = "uk", max_age_minutes: int = 10) -> Dict:
    holdings = list(UserCryptoAsset.objects.filter(user=user))
    if not holdings:
        raise ValueError("Portfolio is empty")

    snapshots: List[Dict] = []
    total_value = 0.0
    refreshed_any = False

    for asset in holdings:
        price_obj, refreshed = _snapshot_for_portfolio(asset, max_age_minutes)
        refreshed_any = refreshed_any or refreshed
        if not price_obj:
            continue

        price = float(price_obj.price)
        value = float(asset.amount) * price
        total_value += value
        snapshots.append(
            {
                "symbol": asset.crypto.symbol,
                "amount": float(asset.amount),
                "price": price,
                "value": value,
                "timestamp": price_obj.timestamp.isoformat(),
                "volume_24h": price_obj.volume_24h,
                "market_cap": price_obj.market_cap,
                "percent_change_1h": price_obj.percent_change_1h,
                "percent_change_24h": price_obj.percent_change_24h,
                "percent_change_7d": price_obj.percent_change_7d,
            }
        )

    if not snapshots:
        raise ValueError("No market data available for portfolio assets")
    for item in snapshots:
        item["weight_pct"] = round((item["value"] / total_value) * 100, 2) if total_value else 0.0

    prompt = _build_portfolio_prompt(snapshots, lang)
    analysis_text = call_gemini(prompt)

    latest_ts = max(item["timestamp"] for item in snapshots)

    return {
        "total_value": round(total_value, 2),
        "items": snapshots,
        "analysis": analysis_text,
        "latest_timestamp": latest_ts,
        "refreshed_any": refreshed_any,
    }


def analyze_portfolio_openai(user, lang: str = "uk", max_age_minutes: int = 10) -> Dict:
    holdings = list(UserCryptoAsset.objects.filter(user=user))
    if not holdings:
        raise ValueError("Portfolio is empty")

    snapshots: List[Dict] = []
    total_value = 0.0
    refreshed_any = False

    for asset in holdings:
        price_obj, refreshed = _snapshot_for_portfolio(asset, max_age_minutes)
        refreshed_any = refreshed_any or refreshed
        if not price_obj:
            continue

        price = float(price_obj.price)
        value = float(asset.amount) * price
        total_value += value
        snapshots.append(
            {
                "symbol": asset.crypto.symbol,
                "amount": float(asset.amount),
                "price": price,
                "value": value,
                "timestamp": price_obj.timestamp.isoformat(),
                "volume_24h": price_obj.volume_24h,
                "market_cap": price_obj.market_cap,
                "percent_change_1h": price_obj.percent_change_1h,
                "percent_change_24h": price_obj.percent_change_24h,
                "percent_change_7d": price_obj.percent_change_7d,
            }
        )

    if not snapshots:
        raise ValueError("No market data available for portfolio assets")

    for item in snapshots:
        item["weight_pct"] = round((item["value"] / total_value) * 100, 2) if total_value else 0.0

    prompt = _build_portfolio_prompt(snapshots, lang)
    analysis_text = call_openai(prompt)

    latest_ts = max(item["timestamp"] for item in snapshots)

    return {
        "total_value": round(total_value, 2),
        "items": snapshots,
        "analysis": analysis_text,
        "latest_timestamp": latest_ts,
        "refreshed_any": refreshed_any,
    }
