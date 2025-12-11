from datetime import datetime
from typing import Dict, Iterable, List, Optional

from django.utils import timezone

from api.models import CryptoAsset, CryptoPrice
from api.serializers import CryptoPriceSerializer


def _get_asset(symbol: str) -> CryptoAsset:
    return CryptoAsset.objects.get(symbol=symbol.upper())


def get_last_points(symbol: str, limit: int = 100) -> List[CryptoPrice]:
    asset = _get_asset(symbol)
    qs = CryptoPrice.objects.filter(asset=asset).order_by("-timestamp")[:limit]
    return list(reversed(qs))


def get_period(symbol: str, start: datetime, end: Optional[datetime] = None) -> List[CryptoPrice]:
    asset = _get_asset(symbol)
    filters: Dict = {"asset": asset, "timestamp__gte": start}
    if end:
        filters["timestamp__lte"] = end
    qs = CryptoPrice.objects.filter(**filters).order_by("timestamp")
    return list(qs)


def serialize_for_chart(points: Iterable[CryptoPrice]) -> List[Dict]:
    serialized = []
    for point in points:
        serialized.append(
            {
                "timestamp": point.timestamp,
                "price": point.price,
                "open": point.open_price,
                "high": point.high_price,
                "low": point.low_price,
                "close": point.close_price,
                "volume_24h": point.volume_24h,
            }
        )
    return serialized


def serialize_for_rest(points: Iterable[CryptoPrice]) -> List[Dict]:
    return CryptoPriceSerializer(points, many=True).data


def build_ws_snapshot(point: CryptoPrice) -> Dict:
    return {
        "symbol": point.asset.symbol,
        "price": float(point.price),
        "timestamp": point.timestamp.isoformat(),
        "volume_24h": float(point.volume_24h) if point.volume_24h is not None else None,
        "open": float(point.open_price) if point.open_price is not None else None,
        "high": float(point.high_price) if point.high_price is not None else None,
        "low": float(point.low_price) if point.low_price is not None else None,
        "close": float(point.close_price) if point.close_price is not None else None,
    }


def get_latest_point(symbol: str) -> Optional[CryptoPrice]:
    asset = _get_asset(symbol)
    return CryptoPrice.objects.filter(asset=asset).order_by("-timestamp").first()


def select_for_period_or_latest(symbol: str, start: Optional[datetime], end: Optional[datetime], limit: int) -> List[CryptoPrice]:
    if start:
        return get_period(symbol, start, end)
    return get_last_points(symbol, limit=limit)


def now_utc() -> datetime:
    return timezone.now()
