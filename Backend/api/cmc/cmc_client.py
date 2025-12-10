from datetime import datetime
from typing import Dict, Iterable, List, Optional

import requests
from django.conf import settings


BASE_URL = "https://pro-api.coinmarketcap.com/v1"
QUOTES_ENDPOINT = "cryptocurrency/quotes/latest"
OHLCV_ENDPOINT = "cryptocurrency/ohlcv/latest"


class CMCError(Exception):
    pass


def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class CMCClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or settings.CMC_API_KEY
        self.session = session or requests.Session()

    def _request(self, path: str, params: Dict) -> Dict:
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        url = f"{BASE_URL}/{path}"

        try:
            resp = self.session.get(url, headers=headers, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            raise CMCError(f"Network error while requesting CMC: {exc}") from exc

        json_data = resp.json()
        status = json_data.get("status", {})
        error_code = status.get("error_code")

        if error_code not in (0, None):
            raise CMCError(f"CMC error {error_code}: {status.get('error_message')}")

        return json_data.get("data", {})

    @staticmethod
    def _normalize_symbols(symbols: Iterable[str]) -> List[str]:
        return [s.upper() for s in symbols]

    def get_quotes(self, symbols: Iterable[str]) -> Dict[str, Dict]:
        sym_list = self._normalize_symbols(symbols)
        params = {"symbol": ",".join(sym_list), "convert": "USD"}
        data = self._request(QUOTES_ENDPOINT, params)
        return {sym: data.get(sym) for sym in sym_list if data.get(sym)}

    def get_quote(self, symbol: str) -> Dict:
        symbol_upper = symbol.upper()
        quotes = self.get_quotes([symbol_upper])
        if symbol_upper not in quotes:
            raise CMCError(f"Symbol '{symbol_upper}' not found in CMC response.")
        return quotes[symbol_upper]

    def get_ohlcv_latest(self, symbols: Iterable[str]) -> Dict[str, Dict]:
        sym_list = self._normalize_symbols(symbols)
        params = {"symbol": ",".join(sym_list), "convert": "USD"}
        data = self._request(OHLCV_ENDPOINT, params)
        return {sym: data.get(sym) for sym in sym_list if data.get(sym)}

    def get_single_ohlcv(self, symbol: str) -> Dict:
        symbol_upper = symbol.upper()
        data = self.get_ohlcv_latest([symbol_upper])
        if symbol_upper not in data:
            raise CMCError(f"Symbol '{symbol_upper}' not found in CMC OHLCV response.")
        return data[symbol_upper]


def _extract_usd_quote(quote_payload: Dict) -> Dict:
    usd = quote_payload.get("quote", {}).get("USD", {})
    if not usd:
        raise CMCError("USD quote not found in CMC payload.")
    return usd


def normalize_quote_payload(symbol: str, quote_payload: Dict, ohlcv_payload: Optional[Dict] = None) -> Dict:
    usd_quote = _extract_usd_quote(quote_payload)
    usd_ohlcv = None
    if ohlcv_payload:
        usd_ohlcv = ohlcv_payload.get("quote", {}).get("USD", {})

    timestamp = parse_timestamp(usd_quote.get("last_updated"))
    if usd_ohlcv and usd_ohlcv.get("timestamp"):
        timestamp = parse_timestamp(usd_ohlcv.get("timestamp")) or timestamp

    return {
        "symbol": symbol.upper(),
        "price": usd_quote["price"],
        "market_cap": usd_quote.get("market_cap"),
        "volume_24h": usd_quote.get("volume_24h"),

        "open": (usd_ohlcv or {}).get("open"),
        "high": (usd_ohlcv or {}).get("high"),
        "low": (usd_ohlcv or {}).get("low"),
        "close": (usd_ohlcv or {}).get("close"),

        "percent_change_1h": usd_quote.get("percent_change_1h"),
        "percent_change_24h": usd_quote.get("percent_change_24h"),
        "percent_change_7d": usd_quote.get("percent_change_7d"),
        "percent_change_30d": usd_quote.get("percent_change_30d"),
        "percent_change_60d": usd_quote.get("percent_change_60d"),
        "percent_change_90d": usd_quote.get("percent_change_90d"),

        "market_dominance": usd_quote.get("market_dominance"),
        "circulating_supply": usd_quote.get("circulating_supply"),
        "total_supply": usd_quote.get("total_supply"),
        "max_supply": usd_quote.get("max_supply"),

        "timestamp": timestamp,
    }


def get_cmc_data(symbol: str) -> Dict:
    client = CMCClient()
    quote = client.get_quote(symbol)
    normalized = normalize_quote_payload(symbol, quote)
    return normalized
