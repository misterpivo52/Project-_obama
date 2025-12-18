from decimal import Decimal
from django.conf import settings
from django.db import transaction
from rest_framework import status

from api.cmc.dashboard_service import get_latest_point
from api.cmc.services import fetch_and_save_full
from api.models import CryptoAsset
from users.models import User, UserCryptoAsset


class SwapError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.status_code = status_code


class SwapService:
    FEE_PCT = Decimal("0.02")

    def _fetch_price(self, symbol: str):
        try:
            price_point = get_latest_point(symbol)
        except Exception:
            price_point = None
        if price_point:
            return price_point
        return fetch_and_save_full(symbol)

    def _calculate(self, user, from_symbol: str, to_symbol: str, amount_in: Decimal, perform: bool):
        from_symbol = (from_symbol or "").upper().strip()
        to_symbol = (to_symbol or "").upper().strip()

        if not from_symbol or not to_symbol:
            raise SwapError("Both from_symbol and to_symbol are required")
        if from_symbol == to_symbol:
            raise SwapError("Symbols must differ")
        if amount_in <= 0:
            raise SwapError("Amount must be greater than zero")

        try:
            from_price = self._fetch_price(from_symbol)
        except Exception as exc:
            raise SwapError(f"Failed to fetch {from_symbol}: {exc}")

        try:
            to_price = self._fetch_price(to_symbol)
        except Exception as exc:
            raise SwapError(f"Failed to fetch {to_symbol}: {exc}")

        rate = Decimal(from_price.price) / Decimal(to_price.price)
        fee_amount = amount_in * self.FEE_PCT
        amount_out = (amount_in - fee_amount) * rate

        result = {
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "amount_in": str(amount_in),
            "amount_out": str(amount_out),
            "fee_amount": str(fee_amount),
            "fee_pct": str(self.FEE_PCT),
            "rate": str(rate),
            "timestamp": to_price.timestamp,
        }

        if not perform:
            return result

        with transaction.atomic():
            try:
                from_asset = UserCryptoAsset.objects.select_for_update().get(
                    user=user, crypto__symbol=from_symbol
                )
            except UserCryptoAsset.DoesNotExist:
                raise SwapError("Not enough balance")

            if from_asset.amount < amount_in:
                raise SwapError("Not enough balance")

            to_crypto, _ = CryptoAsset.objects.get_or_create(symbol=to_symbol, defaults={"name": to_symbol})
            from_crypto = from_asset.crypto

            from_asset.amount = from_asset.amount - amount_in
            from_asset.save(update_fields=["amount"])

            to_record, _ = UserCryptoAsset.objects.select_for_update().get_or_create(
                user=user, crypto=to_crypto, defaults={"amount": Decimal("0")}
            )
            to_record.amount = (to_record.amount or Decimal("0")) + amount_out
            to_record.save(update_fields=["amount"])

            admin_user = None
            admin_email = getattr(settings, "FEE_ADMIN_EMAIL", None)
            if admin_email:
                admin_user = User.objects.filter(email=admin_email).first()
            if not admin_user:
                admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                admin_fee_record, _ = UserCryptoAsset.objects.select_for_update().get_or_create(
                    user=admin_user, crypto=from_crypto, defaults={"amount": Decimal("0")}
                )
                admin_fee_record.amount = (admin_fee_record.amount or Decimal("0")) + fee_amount
                admin_fee_record.save(update_fields=["amount"])
            else:
                raise SwapError("Admin account not configured for fee credit", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return result

    def preview(self, user, from_symbol: str, to_symbol: str, amount_in: Decimal):
        return self._calculate(user, from_symbol, to_symbol, amount_in, perform=False)

    def execute(self, user, from_symbol: str, to_symbol: str, amount_in: Decimal):
        return self._calculate(user, from_symbol, to_symbol, amount_in, perform=True)
