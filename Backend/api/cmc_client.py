import requests
from django.conf import settings


def get_cmc_data(symbol: str) -> dict:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": settings.CMC_API_KEY}
    params = {"symbol": symbol.upper(), "convert": "USD"}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    data = response.json()["data"][symbol.upper()]["quote"]["USD"]

    return {
        "price": data["price"],
        "market_cap": data.get("market_cap"),
        "volume_24h": data.get("volume_24h"),

        "open": data.get("open"),
        "high": data.get("high"),
        "low": data.get("low"),
        "close": data.get("close"),

        "percent_change_1h": data.get("percent_change_1h"),
        "percent_change_24h": data.get("percent_change_24h"),
        "percent_change_7d": data.get("percent_change_7d"),
        "percent_change_30d": data.get("percent_change_30d"),
        "percent_change_60d": data.get("percent_change_60d"),
        "percent_change_90d": data.get("percent_change_90d"),

        "market_dominance": data.get("market_dominance"),
        "circulating_supply": data.get("circulating_supply"),
        "total_supply": data.get("total_supply"),
        "max_supply": data.get("max_supply"),

        "timestamp": data.get("last_updated"),
    }
