from decimal import Decimal

from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    available_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    locked_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_profit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def total_balance(self):
        return self.available_balance + self.locked_balance

    def __str__(self):
        return f"{self.user.email} Wallet"
    
    
    
class InvestmentPlan(models.Model):

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    minimum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    maximum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    roi_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    duration_days = models.PositiveIntegerField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name