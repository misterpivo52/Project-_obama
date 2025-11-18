from django.db import models
from django.contrib.auth.models import User
from api.models import CryptoAsset


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    favorite_crypto = models.ForeignKey(
        CryptoAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="favorite_of",
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


class UserCryptoAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolio")
    crypto = models.ForeignKey(CryptoAsset, on_delete=models.CASCADE, related_name="holders")
    amount = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ("user", "crypto")

    def __str__(self):
        return f"{self.user.username} owns {self.amount} {self.crypto.symbol}"
