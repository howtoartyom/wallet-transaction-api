"""Models for the wallet_transaction_api application."""

from decimal import Decimal

from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class Wallet(models.Model):
    """
    Represents a Wallet with a label and balance.

    Attributes:
        label (str): The name or identifier of the wallet.
        balance (Decimal): The balance amount in wallet, validated to be non-negative.
    """

    label = models.CharField(max_length=100, db_index=True)
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    version = models.IntegerField(default=0)

    class Meta:
        """
        Meta options for the Wallet model.

        Constraints:
            wallet_balance_non_negative: Ensures wallet balance is never negative.
        """

        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0), name="wallet_balance_non_negative"
            ),
        ]

    def __str__(self):
        return f"{self.label} - Balance: {self.balance}"

    def save(self, *args, **kwargs):
        """
        Save the wallet instance, updating the version for optimistic locking.

        Raises:
            ValueError: If the wallet has been modified since it was last read.
        """

        if self.pk:
            # Ensure the balance is still valid
            old_version = Wallet.objects.get(pk=self.pk).version
            if old_version != self.version:
                raise ValueError(
                    "Conflict: The wallet has been modified since it was last read."
                )

            self.version += 1

        super().save(*args, **kwargs)

    def get_balance(self):
        """
        Retrieve the cached balance of the wallet.

        Returns:
            Decimal:Wallet balance from cache (if available).
        """

        cache_key = f"wallet_balance_{self.pk}"
        balance = cache.get(cache_key)
        if balance is None:
            balance = self.balance
            cache.set(
                cache_key, balance, timeout=60 * 5
            )  # Consider a more granular timeout
        return balance


class Transaction(models.Model):
    """
    Represents a financial transaction associated with a Wallet.

    Attributes:
        wallet (Wallet): The wallet associated with the transaction.
        txid (str): A unique transaction identifier.
        amount (Decimal): The amount of the transaction.
        timestamp (datetime): The time the transaction was created.
    """

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    txid = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for the Transaction model.

        Ordering:
            -amount: Orders transactions by amount in descending order by default.
        """

        ordering = ["-amount"]

    def __str__(self):
        return f"Transaction {self.txid} for wallet {self.wallet.label}"

    def save(self, *args, **kwargs):
        """
        Save the transaction and update the associated wallet's balance.

        Raises:
            ValueError: If the transaction would result in a negative wallet balance.
        """

        if self.wallet.balance + self.amount < 0:
            raise ValueError("Wallet balance cannot be negative")
        self.wallet.balance += self.amount
        self.wallet.save()
        super().save(*args, **kwargs)


@receiver([post_save, post_delete], sender=Transaction)
def invalidate_wallet_cache(sender, instance, **kwargs):
    """
    Invalidate the wallet balance cache after a transaction is saved or deleted.

    Args:
        sender (class): The model class that sent the signal.
        instance (Transaction): Transaction instance triggering the signal.
        **kwargs: Additional keyword arguments passed to the signal handler.
    """

    cache_key = f"wallet_balance_{instance.wallet.pk}"
    cache.delete(cache_key)
