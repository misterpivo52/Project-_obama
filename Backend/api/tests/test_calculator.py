from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import CryptoAsset, CryptoPrice
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="calc@test.com",
        password="StrongPass123",
        first_name="Calc",
        last_name="User",
        country="UA",
        phone="+3800000020",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def btc_price(db):
    asset = CryptoAsset.objects.create(symbol="BTC", name="Bitcoin")
    return CryptoPrice.objects.create(
        asset=asset,
        price=Decimal("25000"),
        timestamp=timezone.now(),
    )


def test_calculator_success_existing_price(auth_client, btc_price):
    resp = auth_client.post(
        "/api/calculator/",
        {"symbol": "BTC", "amount": "2"},
        format="json",
    )
    assert resp.status_code == 200
    assert Decimal(resp.data["total_value"]) == Decimal("50000")


def test_calculator_invalid_amount(auth_client):
    resp = auth_client.post(
        "/api/calculator/",
        {"symbol": "BTC", "amount": "0"},
        format="json",
    )
    assert resp.status_code == 400


def test_calculator_missing_symbol(auth_client):
    resp = auth_client.post(
        "/api/calculator/",
        {"amount": "1"},
        format="json",
    )
    assert resp.status_code == 400


def test_calculator_fetch_if_missing(monkeypatch, auth_client):
    from api import views as api_views

    def fake_fetch(symbol):
        asset, _ = CryptoAsset.objects.get_or_create(symbol=symbol, defaults={"name": symbol})
        return CryptoPrice.objects.create(
            asset=asset,
            price=Decimal("123"),
            timestamp=timezone.now(),
        )

    monkeypatch.setattr(api_views, "fetch_and_save_full", fake_fetch)

    resp = auth_client.post(
        "/api/calculator/",
        {"symbol": "NEW", "amount": "2"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["total_value"] == str(Decimal("246"))
