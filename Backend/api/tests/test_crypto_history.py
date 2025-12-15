import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import CryptoAsset, CryptoPrice
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="chart@test.com",
        password="StrongPass123",
        first_name="Chart",
        last_name="User",
        country="UA",
        phone="+3800000040",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_history_unknown_asset(auth_client):
    resp = auth_client.get("/api/crypto/UNKNOWN/history/")
    assert resp.status_code == 404


def test_history_limit(auth_client):
    asset = CryptoAsset.objects.create(symbol="AAA", name="AAA")
    for i in range(3):
        CryptoPrice.objects.create(
            asset=asset,
            price=Decimal("1") + i,
            timestamp=timezone.now(),
        )
    resp = auth_client.get("/api/crypto/AAA/history/?limit=2")
    assert resp.status_code == 200
    assert len(resp.data) == 2
