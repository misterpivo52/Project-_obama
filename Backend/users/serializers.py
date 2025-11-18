from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import CryptoAsset
from .models import UserProfile, UserCryptoAsset


class CryptoAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoAsset
        fields = ["id", "symbol", "name"]


class UserCryptoAssetSerializer(serializers.ModelSerializer):
    crypto = CryptoAssetSerializer()

    class Meta:
        model = UserCryptoAsset
        fields = ["crypto", "amount"]


class UserProfileSerializer(serializers.ModelSerializer):
    favorite_crypto = CryptoAssetSerializer()

    class Meta:
        model = UserProfile
        fields = ["favorite_crypto"]


class UserPortfolioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCryptoAsset
        fields = ["crypto", "amount"]
