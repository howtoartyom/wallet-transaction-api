"""Test cases for the API endpoints in the wallet_transaction_api application."""

import json
from decimal import Decimal

import pytest
from loguru import logger
from rest_framework import status

from wallet_transaction_api.models import Transaction, Wallet

CONTENT_TYPE = "application/vnd.api+json"
DATA = "data"
ATTRIBUTES = "attributes"
TYPE = "type"
DETAIL = "detail"


@pytest.mark.django_db
def test_wallet_list_api(api_client):
    """Test case for retrieving the list of wallets via the API."""
    Wallet.objects.create(label="Wallet 1", balance=Decimal("100.00"))
    Wallet.objects.create(label="Wallet 2", balance=Decimal("200.00"))

    logger.info("Fetching list of wallets...")
    response = api_client.get("/api/wallets/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()[DATA]) == 2


@pytest.mark.django_db
def test_transaction_list_api(api_client, create_wallet):
    """Test case for retrieving the list of transactions via the API."""
    wallet = create_wallet()
    Transaction.objects.create(wallet=wallet, txid="TX123", amount=Decimal("50.00"))
    Transaction.objects.create(wallet=wallet, txid="TX124", amount=Decimal("75.00"))

    logger.info("Fetching list of transactions...")
    response = api_client.get("/api/transactions/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()[DATA]) == 2


@pytest.mark.django_db
def test_wallet_update_api(api_client, create_wallet):
    """Test case for updating a wallet via the API."""
    wallet = create_wallet()

    update_data = {
        DATA: {
            TYPE: "Wallet",
            "id": wallet.id,
            ATTRIBUTES: {"label": "Updated Wallet", "balance": "150.00"},
        }
    }
    logger.info(f"Updating wallet with ID {wallet.id}...")
    response = api_client.patch(
        f"/api/wallets/{wallet.id}/",
        data=json.dumps(update_data),
        content_type=CONTENT_TYPE,
    )

    assert response.status_code == status.HTTP_200_OK
    wallet.refresh_from_db()
    assert wallet.label == "Updated Wallet"
    assert wallet.balance == Decimal("150.00")

    # Additional data integrity checks
    response_data = response.json()[DATA]
    assert response_data[ATTRIBUTES]["label"] == "Updated Wallet"
    assert Decimal(response_data[ATTRIBUTES]["balance"]) == Decimal("150.00")


@pytest.mark.django_db
def test_wallet_delete_api(api_client, create_wallet):
    """Test case for deleting a wallet via the API."""
    wallet = create_wallet()

    logger.info(f"Deleting wallet with ID {wallet.id}...")
    response = api_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Wallet.objects.filter(id=wallet.id).count() == 0
    logger.success(f"Wallet with ID {wallet.id} successfully deleted.")


@pytest.mark.django_db
def test_transaction_delete_api(api_client, create_wallet):
    """Test case for deleting a transaction via the API."""
    wallet = create_wallet()
    transaction = Transaction.objects.create(
        wallet=wallet, txid="TX123", amount=Decimal("50.00")
    )

    logger.info(f"Deleting transaction with ID {transaction.id}...")
    response = api_client.delete(f"/api/transactions/{transaction.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Transaction.objects.filter(id=transaction.id).count() == 0
    logger.success(f"Transaction with ID {transaction.id} successfully deleted.")


@pytest.mark.django_db
def test_pagination(api_client, create_wallet):
    """Test case for pagination in the API."""
    wallet = create_wallet()
    for i in range(15):
        Transaction.objects.create(
            wallet=wallet, txid=f"TX{i+1: 03d}", amount=Decimal(f"{i+1}.00")
        )

    logger.info("Testing pagination for transactions...")
    response = api_client.get("/api/transactions/?page=2")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()[DATA]) == 5  # Assuming default page size is 10


@pytest.mark.django_db
def test_ordering_filtering(api_client, create_wallet):
    """Test case for ordering and filtering in the API."""
    wallet1 = create_wallet(label="Wallet 1", balance=Decimal("100.00"))
    wallet2 = create_wallet(label="Wallet 2", balance=Decimal("200.00"))

    Transaction.objects.create(wallet=wallet1, txid="TX001", amount=Decimal("50.00"))
    Transaction.objects.create(wallet=wallet2, txid="TX002", amount=Decimal("75.00"))

    logger.info("Testing ordering of transactions by amount descending...")
    response = api_client.get("/api/transactions/?ordering=-amount")
    response_data = response.json()
    logger.info(response_data)

    assert response_data[DATA][0][ATTRIBUTES]["txid"] == "TX002"
    assert response_data[DATA][1][ATTRIBUTES]["txid"] == "TX001"


@pytest.mark.django_db
def test_unique_txid_validation(api_client, create_wallet):
    """Test case for unique txid validation."""
    wallet = create_wallet()
    Transaction.objects.create(wallet=wallet, txid="TX123", amount=Decimal("50.00"))

    duplicate_tx_data = {
        DATA: {
            TYPE: "Transaction",
            ATTRIBUTES: {
                "txid": "TX123",
                "amount": "25.00",
                "wallet": wallet.id,
            },
        }
    }
    logger.info("Testing unique constraint on txid field...")
    response = api_client.post(
        "/api/transactions/",
        data=json.dumps(duplicate_tx_data),
        content_type=CONTENT_TYPE,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert DETAIL in response.data["errors"][0]


@pytest.mark.django_db
def test_transaction_creation_for_nonexistent_wallet(api_client):
    """Test case for handling creation of a transaction for a nonexistent wallet."""
    non_existent_wallet_id = 9999

    invalid_data = {
        DATA: {
            TYPE: "Transaction",
            ATTRIBUTES: {
                "txid": "TX123",
                "amount": "50.00",
                "wallet": non_existent_wallet_id,
            },
        }
    }
    logger.info("Testing transaction creation with nonexistent wallet...")
    response = api_client.post(
        "/api/transactions/",
        data=json.dumps(invalid_data),
        content_type=CONTENT_TYPE,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert DETAIL in response.data["errors"][0]


@pytest.mark.django_db
def test_transaction_creation_with_negative_balance_api(api_client, create_wallet):
    """Test case for creating a transaction via API with a negative amount."""
    wallet = create_wallet()

    negative_transaction_data = {
        DATA: {
            TYPE: "Transaction",
            ATTRIBUTES: {
                "txid": "NEG_TX",
                "amount": "-150.00",
                "wallet": wallet.id,
            },
        }
    }

    logger.info(
        "Testing transaction creation that would result in a negative balance..."
    )
    response = api_client.post(
        "/api/transactions/",
        data=json.dumps(negative_transaction_data),
        content_type=CONTENT_TYPE,
    )

    error_message = response.data.get("errors", [{}])[0].get(DETAIL)

    assert (
        error_message
    ), f"Expected error message but found none. Response data: {response.data}"
    assert (
        "Wallet balance cannot be negative" in error_message
    ), f"Unexpected error message: {error_message}"
    logger.success("Negative balance transaction was correctly rejected.")
