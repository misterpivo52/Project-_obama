from rest_framework import serializers
from .models import CryptoAsset, CryptoPrice


class CryptoAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoAsset
        fields = ["id", "symbol", "name"]


class CryptoPriceSerializer(serializers.ModelSerializer):
    asset = serializers.CharField(source="asset.symbol")

    class Meta:
        model = CryptoPrice
        fields = [
            "asset",
            "price",
            "market_cap",
            "volume_24h",

            "open_price",
            "high_price",
            "low_price",
            "close_price",

            "percent_change_1h",
            "percent_change_24h",
            "percent_change_7d",
            "percent_change_30d",
            "percent_change_60d",
            "percent_change_90d",

            "market_dominance",
            "circulating_supply",
            "total_supply",
            "max_supply",

            "timestamp",
        ]
