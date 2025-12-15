import os
import django
import pytest
from rest_framework.test import APIClient
from users.models import User


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto.settings")

django.setup()

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        email="testuser@example.com",
        password="StrongPass123",
        first_name="Test",
        last_name="User",
        country="UA",
        phone="+3800000099",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client
