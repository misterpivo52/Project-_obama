from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from users.models import User, UserCryptoAsset
from api.models import CryptoAsset


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="port@test.com",
        password="StrongPass123",
        first_name="Port",
        last_name="User",
        country="UA",
        phone="+3800000010",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def btc(db):
    return CryptoAsset.objects.create(symbol="BTC", name="Bitcoin")


def test_add_by_symbol_success(auth_client, user):
    resp = auth_client.post(
        "/auth/portfolio/add/",
        {"symbol": "BTC", "amount": "1.5"},
        format="json",
    )
    assert resp.status_code == 200
    record = UserCryptoAsset.objects.get(user=user, crypto__symbol="BTC")
    assert record.amount == Decimal("1.5")


def test_add_invalid_amount(auth_client):
    resp = auth_client.post(
        "/auth/portfolio/add/",
        {"symbol": "BTC", "amount": "0"},
        format="json",
    )
    assert resp.status_code == 400


def test_remove_more_than_have(auth_client, user, btc):
    UserCryptoAsset.objects.create(user=user, crypto=btc, amount=Decimal("2"))
    resp = auth_client.post(
        "/auth/portfolio/remove/",
        {"symbol": "BTC", "amount": "5"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data.get("amount") == "0"
    assert not UserCryptoAsset.objects.filter(user=user, crypto=btc).exists()


def test_portfolio_requires_auth():
    client = APIClient()
    resp = client.get("/auth/portfolio/")
    assert resp.status_code in (401, 403)


def test_favorite_set_success(auth_client, btc, user):
    resp = auth_client.post(
        "/auth/favorite/",
        {"crypto": btc.id},
        format="json",
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.profile.favorite_crypto == btc


def test_dashboard_symbol_invalid(monkeypatch, auth_client):
    resp = auth_client.post(
        "/auth/dashboard/symbol/",
        {"symbol": ""},
        format="json",
    )
    assert resp.status_code == 400


def test_dashboard_symbol_success(monkeypatch, auth_client):
    from users import views as user_views
    from api.models import CryptoAsset, CryptoPrice
    from django.utils import timezone

    def fake_fetch(symbol):
        asset, _ = CryptoAsset.objects.get_or_create(symbol=symbol, defaults={"name": symbol})
        return CryptoPrice.objects.create(asset=asset, price=Decimal("100"), timestamp=timezone.now())

    monkeypatch.setattr(user_views, "fetch_and_save_full", fake_fetch)

    resp = auth_client.post(
        "/auth/dashboard/symbol/",
        {"symbol": "ETH"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data.get("symbol") == "ETH"
