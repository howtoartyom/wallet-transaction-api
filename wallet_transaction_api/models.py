from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Wallet(models.Model):
    label = models.CharField(max_length=100)
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def __str__(self):
        return f"{self.label} - Balance: {self.balance}"


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    txid = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.txid} for wallet {self.wallet.label}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.wallet.balance += self.amount
            if self.wallet.balance < 0:
                raise ValueError("Wallet balance cannot be negative")
            self.wallet.save()
        super().save(*args, **kwargs)
