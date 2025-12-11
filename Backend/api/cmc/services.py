from typing import Dict, Optional

from django.utils.timezone import now

from api.cmc.cmc_client import CMCClient, CMCError, normalize_quote_payload
from api.models import CryptoAsset, CryptoPrice


def save_cmc_data(symbol: str, data: Dict) -> CryptoPrice:
    asset, _ = CryptoAsset.objects.get_or_create(
        symbol=symbol.upper(),
        defaults={"name": symbol.upper()},
    )

    price_obj = CryptoPrice.objects.create(
        asset=asset,
        price=data["price"],
        market_cap=data.get("market_cap"),
        volume_24h=data.get("volume_24h"),
        open_price=data.get("open"),
        high_price=data.get("high"),
        low_price=data.get("low"),
        close_price=data.get("close"),
        percent_change_1h=data.get("percent_change_1h"),
        percent_change_24h=data.get("percent_change_24h"),
        percent_change_7d=data.get("percent_change_7d"),
        percent_change_30d=data.get("percent_change_30d"),
        percent_change_60d=data.get("percent_change_60d"),
        percent_change_90d=data.get("percent_change_90d"),
        market_dominance=data.get("market_dominance"),
        circulating_supply=data.get("circulating_supply"),
        total_supply=data.get("total_supply"),
        max_supply=data.get("max_supply"),
        timestamp=data.get("timestamp", now()),
    )

    return price_obj


def fetch_and_save_quote(symbol: str) -> CryptoPrice:
    client = CMCClient()
    quote_payload = client.get_quote(symbol)
    normalized = normalize_quote_payload(symbol, quote_payload)
    return save_cmc_data(symbol, normalized)

def fetch_and_save_full(symbol: str) -> CryptoPrice:
    client = CMCClient()
    quote_payload = client.get_quote(symbol)
    ohlcv_payload: Optional[Dict] = None
    try:
        ohlcv_payload = client.get_single_ohlcv(symbol)
    except CMCError:
        ohlcv_payload = None

    normalized = normalize_quote_payload(symbol, quote_payload, ohlcv_payload)
    return save_cmc_data(symbol, normalized)


def merge_quote_and_ohlcv(symbol: str, quote_payload: Dict, ohlcv_payload: Optional[Dict]) -> Dict:
    return normalize_quote_payload(symbol, quote_payload, ohlcv_payload)
