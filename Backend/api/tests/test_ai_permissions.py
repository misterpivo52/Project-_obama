import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="ai@test.com",
        password="StrongPass123",
        first_name="AI",
        last_name="User",
        country="UA",
        phone="+3800000030",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_ai_requires_auth():
    client = APIClient()
    endpoints = [
        ("/api/openai/analysis/", {"symbol": "ETH"}),
        ("/api/openai/portfolio/", None),
    ]
    for path, payload in endpoints:
        if payload:
            resp = client.post(path, payload, format="json")
        else:
            resp = client.get(path)
        assert resp.status_code in (401, 403)


def test_ai_happy_path(monkeypatch, auth_client):
    from api import ai_views

    def fake_symbol(symbol, lang="uk"):
        return {"symbol": symbol, "summary": "ok"}

    def fake_portfolio(user, lang="uk"):
        return {"portfolio": []}

    monkeypatch.setattr(ai_views, "analyze_symbol", fake_symbol)
    monkeypatch.setattr(ai_views, "analyze_portfolio", fake_portfolio)

    r1 = auth_client.post("/api/openai/analysis/", {"symbol": "BTC"}, format="json")
    r2 = auth_client.get("/api/openai/portfolio/")
    assert r1.status_code == 200
    assert r1.data["symbol"] == "BTC"
    assert r2.status_code == 200
    assert "portfolio" in r2.data
