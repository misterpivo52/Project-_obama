from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from api.models import CryptoAsset
from api.cmc.services import fetch_and_save_full
from users.models import UserProfile, UserCryptoAsset
from users.serializers import (
    UserCryptoAssetSerializer,
    UserPortfolioUpdateSerializer,
    UserProfileSerializer,
)


class UserPortfolioView(APIView):
    def get(self, request):
        user = request.user
        portfolio = UserCryptoAsset.objects.filter(user=user)
        ser = UserCryptoAssetSerializer(portfolio, many=True)
        return Response(ser.data)


class AddCryptoToPortfolioView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")
        amount = float(request.data.get("amount", 0))

        try:
            crypto = CryptoAsset.objects.get(id=crypto_id)
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Crypto not found"}, status=404)

        record, _ = UserCryptoAsset.objects.get_or_create(
            user=user,
            crypto=crypto,
            defaults={"amount": 0},
        )

        record.amount += amount
        record.save()

        return Response({"status": "added", "amount": record.amount})


class RemoveCryptoFromPortfolioView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")
        amount = float(request.data.get("amount", 0))

        try:
            record = UserCryptoAsset.objects.get(user=user, crypto_id=crypto_id)
        except UserCryptoAsset.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)

        record.amount -= amount
        if record.amount < 0:
            record.amount = 0
        record.save()

        return Response({"status": "removed", "amount": record.amount})


class SetFavoriteCryptoView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")

        try:
            crypto = CryptoAsset.objects.get(id=crypto_id)
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Crypto not found"}, status=404)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.favorite_crypto = crypto
        profile.save()

        return Response({"favorite": crypto.symbol})


class SetDashboardCryptoView(APIView):
    def post(self, request):
        user = request.user
        symbol = str(request.data.get("symbol", "")).upper().strip()
        if not symbol:
            return Response({"error": "Symbol is required"}, status=400)

        crypto, _ = CryptoAsset.objects.get_or_create(
            symbol=symbol,
            defaults={"name": symbol},
        )
        try:
            fetch_and_save_full(symbol)
        except Exception as exc:
            return Response({"error": f"Failed to fetch data for {symbol}: {exc}"}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.favorite_crypto = crypto
        profile.save()

        return Response(
            {
                "symbol": symbol,
                "message": f"{symbol} pinned to dashboard",
            }
        )
