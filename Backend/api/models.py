from django.db import models

from django.db import models


class CryptoAsset(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.symbol} ({self.name})"


class CryptoPrice(models.Model):
    asset = models.ForeignKey(CryptoAsset, on_delete=models.CASCADE, related_name="prices")

    price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)

    open_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    high_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    low_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    close_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    percent_change_1h = models.FloatField(null=True, blank=True)
    percent_change_24h = models.FloatField(null=True, blank=True)
    percent_change_7d = models.FloatField(null=True, blank=True)
    percent_change_30d = models.FloatField(null=True, blank=True)
    percent_change_60d = models.FloatField(null=True, blank=True)
    percent_change_90d = models.FloatField(null=True, blank=True)

    market_dominance = models.FloatField(null=True, blank=True)
    circulating_supply = models.FloatField(null=True, blank=True)
    total_supply = models.FloatField(null=True, blank=True)
    max_supply = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.asset.symbol} — {self.price} USD @ {self.timestamp}"

