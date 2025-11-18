from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CryptoPriceSerializer
from .models import CryptoAsset, CryptoPrice
from .services import save_cmc_data
from .cmc_client import get_cmc_data


class CurrentPriceView(APIView):
    def get(self, request, symbol):
        try:
            cmc_data = get_cmc_data(symbol)
            price_obj = save_cmc_data(symbol, cmc_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CryptoPriceSerializer(price_obj).data)


class PriceHistoryView(APIView):
    def get(self, request, symbol):
        limit = int(request.GET.get("limit", 100))

        try:
            asset = CryptoAsset.objects.get(symbol=symbol.upper())
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Unknown asset"}, status=404)

        qs = CryptoPrice.objects.filter(asset=asset).order_by("-timestamp")[:limit]
        data = CryptoPriceSerializer(qs[::-1], many=True).data

        return Response(data)
