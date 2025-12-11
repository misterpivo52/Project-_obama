from typing import Iterable, List, Union

from celery import shared_task
from django.conf import settings

from api.cmc.services import fetch_and_save_full


def _resolve_symbols(symbols: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(symbols, str):
        return [s.strip() for s in symbols.split(",") if s.strip()]
    return [s.strip() for s in symbols if s.strip()]


@shared_task(name="api.cmc.tasks.update_cmc_prices")
def update_cmc_prices(symbols: Union[str, Iterable[str], None] = None):
    target_symbols = symbols or getattr(settings, "CMC_SYMBOLS", ["BTC", "ETH"])
    symbol_list = _resolve_symbols(target_symbols)
    results = []
    for symbol in symbol_list:
        results.append(fetch_and_save_full(symbol))
    return [obj.id for obj in results if obj]
