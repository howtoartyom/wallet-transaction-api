"""Serializers for the wallet_transaction_api application."""

from rest_framework import serializers

from .models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model.

    Converts Wallet instances to JSON format and vice versa.
    """

    class Meta:
        model = Wallet
        fields = ["id", "label", "balance"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "wallet", "txid", "amount", "timestamp"]

    def validate(self, data):
        wallet = data["wallet"]
        amount = data["amount"]

        if wallet.balance + amount < 0:
            raise serializers.ValidationError("Wallet balance cannot be negative")

        return data
