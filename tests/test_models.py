"""Test cases for the models in the wallet_transaction_api application."""

from decimal import Decimal

import pytest
from django.core.cache import cache

from wallet_transaction_api.models import Transaction, Wallet


@pytest.mark.django_db
def test_wallet_creation():
    """Test case for creating a wallet."""
    wallet = Wallet.objects.create(label="Test Wallet", balance=Decimal("100.00"))
    assert wallet.id is not None
    assert wallet.label == "Test Wallet"
    assert wallet.balance == Decimal("100.00")


@pytest.mark.django_db
def test_transaction_creation():
    """Test case for creating a transaction."""
    wallet = Wallet.objects.create(label="Test Wallet", balance=Decimal("100.00"))
    transaction = Transaction.objects.create(
        wallet=wallet, txid="TX123", amount=Decimal("50.00")
    )
    wallet.refresh_from_db()
    transaction.refresh_from_db()
    assert transaction.txid == "TX123"
    assert transaction.amount == Decimal("50.00")
    assert wallet.balance == Decimal("150.00")


@pytest.mark.django_db
def test_transaction_creation_with_negative_amount(wallet_fixture):
    """Test case for creating a transaction with a negative amount."""
    wallet = wallet_fixture

    with pytest.raises(ValueError, match="Wallet balance cannot be negative"):
        Transaction.objects.create(
            wallet=wallet, txid="NEG_TX", amount=Decimal("-150.00")
        )

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("100.00")  # Balance should remain unchanged


@pytest.mark.django_db
def test_cache_invalidation_on_transaction(wallet_fixture):
    """Test case to ensure cache invalidation on transaction creation."""
    wallet = wallet_fixture
    cache_key = f"wallet_balance_{wallet.pk}"

    cache.delete(cache_key)

    initial_balance = wallet.get_balance()
    assert initial_balance == Decimal("100.00")

    Transaction.objects.create(wallet=wallet, txid="TX001", amount=Decimal("50.00"))

    # Verify cache is invalidated
    cached_balance = cache.get(cache_key)
    assert cached_balance is None

    updated_balance = wallet.get_balance()
    assert updated_balance == Decimal("150.00")


@pytest.mark.django_db
def test_transaction_amount_precision():
    """Test case to ensure the amount field precision in transactions."""
    wallet = Wallet.objects.create(label="Test Wallet", balance=Decimal("100.00"))

    transaction = Transaction.objects.create(
        wallet=wallet, txid="PRECISION_TX", amount=Decimal("0.123456789123456789")
    )
    transaction.refresh_from_db()
    assert transaction.amount == Decimal("0.123456789123456789")

    max_value = Decimal("99999999.99999999")
    max_transaction_amount = max_value - wallet.balance
    max_transaction = Transaction.objects.create(
        wallet=wallet, txid="MAX_TX", amount=max_transaction_amount
    )
    max_transaction.refresh_from_db()
    assert max_transaction.amount == max_transaction_amount
    assert wallet.balance == max_value

    min_value = Decimal("1E-18")
    min_transaction = Transaction.objects.create(
        wallet=wallet, txid="MIN_TX", amount=min_value
    )
    min_transaction.refresh_from_db()
    assert min_transaction.amount == min_value


@pytest.fixture
def wallet_fixture():
    """Fixture to create a wallet for reuse in multiple tests."""
    return Wallet.objects.create(label="Test Wallet", balance=Decimal("100.00"))
