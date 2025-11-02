from django.db import models

class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100, help_text="Full name of the cryptocurrency")
    symbol = models.CharField(max_length=10, unique=True, help_text="Ticker symbol")
    current_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, help_text="Current price")
    market_cap = models.BigIntegerField(null=True, blank=True, help_text="Market capitalization")
    last_updated = models.DateTimeField(null=True, blank=True, help_text="Time of last data update")

    def __str__(self):
        return self.name
