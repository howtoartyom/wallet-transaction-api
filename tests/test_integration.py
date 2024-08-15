# test_integration.py
"""Integration test case for wallet-transaction-api."""

import json
from decimal import Decimal

import pytest
from django.core.cache import cache
from loguru import logger
from rest_framework import status
from rest_framework.test import APIClient

# Constants for API response structure
CONTENT_TYPE = "application/vnd.api+json"
DATA = "data"
ATTRIBUTES = "attributes"
TYPE = "type"
DETAIL = "detail"


@pytest.mark.django_db
class TestWalletTransactionAPI:
    """Integration tests for wallet-transaction-api."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for integration tests."""
        self.client = APIClient()

    def create_wallet(self, label="Test Wallet"):
        """Helper function to create a wallet."""
        wallet_data = {
            DATA: {
                TYPE: "Wallet",
                ATTRIBUTES: {"label": label},
            }
        }
        response = self.client.post(
            "/api/wallets/",
            data=json.dumps(wallet_data),
            content_type=CONTENT_TYPE,
        )
        assert response.status_code == status.HTTP_201_CREATED
        return response.json()[DATA]["id"]

    def get_wallet_balance(self, wallet_id):
        """Helper function to get the balance of a wallet."""
        cache_key = f"wallet_balance_{wallet_id}"
        cache.delete(cache_key)
        response = self.client.get(f"/api/wallets/{wallet_id}/")
        assert response.status_code == status.HTTP_200_OK
        return Decimal(response.json()[DATA][ATTRIBUTES]["balance"])

    def create_transaction(self, txid, amount, wallet_id):
        """Helper function to create a transaction."""
        transaction_data = {
            DATA: {
                TYPE: "Transaction",
                ATTRIBUTES: {"txid": txid, "amount": amount, "wallet": wallet_id},
            }
        }
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(transaction_data),
            content_type=CONTENT_TYPE,
        )
        return response

    def assert_error_message(self, response, expected_message):
        """Helper function to assert an error message in the response."""
        response_json = response.json()
        error_message = None

        if "errors" in response_json:
            errors = response_json["errors"]
            if isinstance(errors, dict) and "errors" in errors:
                first_error = errors["errors"][0]
                error_detail = first_error.get(DETAIL, {})
            else:
                first_error = errors[0]
                error_detail = first_error.get(DETAIL, {})

            if isinstance(error_detail, str):
                try:
                    error_detail = json.loads(error_detail)
                except json.JSONDecodeError:
                    pass

            if isinstance(error_detail, dict):
                error_message = error_detail.get("non_field_errors", [None])[0]
            else:
                error_message = error_detail
        elif DETAIL in response_json:
            error_message = response_json[DETAIL]

        assert (
            error_message
        ), f"Expected error message but found none. Response data: {response_json}"
        assert (
            expected_message in error_message
        ), f"Unexpected error message: {error_message}"

    def test_wallet_creation_and_transaction_flow(self):
        """Test the creation of a wallet and perform a series of transactions."""
        wallet_id = self.create_wallet()
        assert self.get_wallet_balance(wallet_id) == Decimal("0.00")

        response = self.create_transaction("TX001", "100.00", wallet_id)
        assert response.status_code == status.HTTP_201_CREATED
        self.get_wallet_balance(wallet_id)
        response = self.create_transaction("TX002", "-50.00", wallet_id)
        assert response.status_code == status.HTTP_201_CREATED
        self.get_wallet_balance(wallet_id)

        # Validate balance after transactions
        final_balance = self.get_wallet_balance(wallet_id)
        logger.info(f"Final balance after transactions: {final_balance}")
        assert final_balance == Decimal("50.00")

        # Attempt a transaction that would result in a negative balance
        transaction_response_3 = self.create_transaction("TX003", "-100.00", wallet_id)
        assert transaction_response_3.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_error_message(
            transaction_response_3, "Wallet balance cannot be negative"
        )

        # Validate balance remains unchanged after failed transaction
        assert self.get_wallet_balance(wallet_id) == Decimal("50.00")

        # Test a zero-amount transaction
        assert (
            self.create_transaction("TX004", "0.00", wallet_id).status_code
            == status.HTTP_201_CREATED
        )
        assert self.get_wallet_balance(wallet_id) == Decimal("50.00")
