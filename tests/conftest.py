"""Configuration file for pytest."""

import os
from decimal import Decimal

import django
import environ
import pytest
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallet_transaction_api.settings")


env = environ.Env()
env.read_env(env_file=os.path.join(os.path.dirname(__file__), "../.env"))

settings.CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

django.setup()


@pytest.fixture
def api_client():
    """Fixture to create and return an APIClient instance."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def create_wallet():
    """Fixture to create and return a wallet instance."""
    from wallet_transaction_api.models import Wallet

    def _create_wallet(label="Test Wallet", balance=Decimal("100.00")):
        return Wallet.objects.create(label=label, balance=balance)

    return _create_wallet
