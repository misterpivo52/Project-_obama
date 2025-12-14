from decimal import Decimal, InvalidOperation

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.models import CryptoAsset
from api.serializers import CryptoPriceSerializer
from api.cmc.dashboard_service import get_last_points, serialize_for_rest, get_latest_point
from api.cmc.services import fetch_and_save_full


class CurrentPriceView(APIView):
    def get(self, request, symbol):
        try:
            price_obj = fetch_and_save_full(symbol)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CryptoPriceSerializer(price_obj).data)


class PriceHistoryView(APIView):
    def get(self, request, symbol):
        limit = int(request.GET.get("limit", 100))

        try:
            points = get_last_points(symbol, limit=limit)
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Unknown asset"}, status=404)

        return Response(serialize_for_rest(points))


class CalculatorView(APIView):
    def post(self, request):
        symbol_raw = request.data.get("symbol", "")
        amount_raw = request.data.get("amount")

        symbol = str(symbol_raw).upper().strip()
        if not symbol:
            return Response({"error": "Symbol is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount_raw))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            price_obj = get_latest_point(symbol)
        except CryptoAsset.DoesNotExist:
            price_obj = None
        if not price_obj:
            try:
                price_obj = fetch_and_save_full(symbol)
            except Exception as exc:
                return Response({"error": f"Failed to fetch data for {symbol}: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        total_value = amount * Decimal(price_obj.price)

        return Response(
            {
                "symbol": symbol,
                "amount": str(amount),
                "price": str(price_obj.price),
                "total_value": str(total_value),
                "timestamp": price_obj.timestamp,
            }
        )
