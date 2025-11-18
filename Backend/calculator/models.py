from django.db import models
from django.contrib.auth.models import User

class CryptoConversion(models.Model):
    """Saving cryptocurrency conversion history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    from_currency = models.CharField(max_length=20)
    to_currency = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    result = models.DecimalField(max_digits=20, decimal_places=8)
    rate = models.DecimalField(max_digits=20, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Crypto Conversions'

    def __str__(self):
        return f'{self.amount} {self.from_currency} -> {self.to_currency}'