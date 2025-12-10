from typing import Iterable, List
from api.cmc.services import fetch_and_save_full


def update_symbols(symbols: Iterable[str]) -> List:
    results = []
    for symbol in symbols:
        results.append(fetch_and_save_full(symbol))
    return results


def update_single(symbol: str):
    return fetch_and_save_full(symbol)
