from django.db import models
from django.contrib.auth.models import User
from api.models import Cryptocurrency


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    followed_cryptos = models.ManyToManyField(
        Cryptocurrency,
        blank=True,
        related_name="followers",
    )

    def __str__(self):
        return f"Profile of {self.user.username}"
