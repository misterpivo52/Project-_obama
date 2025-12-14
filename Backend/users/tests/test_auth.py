import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
def test_register_success():
    client = APIClient()
    r = client.post(
        "/auth/register/",
        {
            "email": "test@test.com",
            "password": "StrongPass123",
            "first_name": "Test",
            "last_name": "User",
            "country": "UA",
            "phone": "+3800000000"
        },
        format="json"
    )
    assert r.status_code == 201
    assert User.objects.filter(email="test@test.com").exists()

@pytest.mark.django_db
def test_login_invalid_credentials():
    client = APIClient()
    r = client.post(
        "/auth/login/",
        {"email": "x@test.com", "password": "123"},
        format="json"
    )
    assert r.status_code == 401

@pytest.mark.django_db
def test_login_requires_email_verification():
    user = User.objects.create_user(
        email="verify@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=False
    )
    client = APIClient()
    r = client.post(
        "/auth/login/",
        {"email": "verify@test.com", "password": "StrongPass123"},
        format="json"
    )
    assert r.status_code == 460

@pytest.mark.django_db
def test_login_without_2fa_returns_tokens():
    user = User.objects.create_user(
        email="plain@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=True,
        two_factor_enabled=False
    )
    client = APIClient()
    r = client.post(
        "/auth/login/",
        {"email": "plain@test.com", "password": "StrongPass123"},
        format="json"
    )
    assert r.status_code == 200
    assert "tokens" in r.data

@pytest.mark.django_db
def test_login_with_2fa_requires_code():
    user = User.objects.create_user(
        email="2fa@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=True,
        two_factor_enabled=True
    )
    client = APIClient()
    r = client.post(
        "/auth/login/",
        {"email": "2fa@test.com", "password": "StrongPass123"},
        format="json"
    )
    assert r.status_code == 409



@pytest.mark.django_db
def test_verify_2fa_invalid_code():
    user = User.objects.create_user(
        email="code@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=True,
        two_factor_enabled=True
    )
    client = APIClient()
    r = client.post(
        "/auth/verify-2fa/",
        {"user_id": str(user.id), "code": "000000"},
        format="json"
    )
    assert r.status_code == 400

@pytest.mark.django_db
def test_verify_2fa_success():
    user = User.objects.create_user(
        email="ok@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=True,
        two_factor_enabled=True
    )
    code = user.generate_verification_code()
    client = APIClient()
    r = client.post(
        "/auth/verify-2fa/",
        {"user_id": str(user.id), "code": code},
        format="json"
    )
    assert r.status_code == 200
    assert "tokens" in r.data

@pytest.mark.django_db
def test_logout_invalid_token():
    client = APIClient()
    r = client.post("/auth/logout/")
    assert r.status_code in (401, 403)

@pytest.mark.django_db
def test_password_reset_request_existing_user():
    user = User.objects.create_user(
        email="reset@test.com",
        password="StrongPass123",
        is_active=True,
        email_verified=True
    )
    client = APIClient()
    r = client.post(
        "/auth/request-password-reset/",
        {"email": "reset@test.com"},
        format="json"
    )
    assert r.status_code == 200

@pytest.mark.django_db
def test_confirm_password_reset_success():
    user = User.objects.create_user(
        email="confirm@test.com",
        password="OldPass123",
        is_active=True,
        email_verified=True
    )
    code = user.generate_verification_code()
    client = APIClient()
    r = client.post(
        "/auth/confirm-password-reset/",
        {
            "email": "confirm@test.com",
            "code": code,
            "new_password": "NewStrongPass123"
        },
        format="json"
    )
    assert r.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123")
