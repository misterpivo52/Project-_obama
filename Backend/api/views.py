from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.models import CryptoAsset
from api.serializers import CryptoPriceSerializer
from api.cmc.dashboard_service import get_last_points, serialize_for_rest
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
