from decimal import Decimal
from django.conf import settings
from django.db import models


class InvestmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    
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
    


class Investment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investments",
    )
    plan = models.ForeignKey(
        InvestmentPlan,
        on_delete=models.PROTECT,
        related_name="investments",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    expected_profit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    total_return = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=InvestmentStatus.choices,
        default=InvestmentStatus.PENDING,
    )
    start_date = models.DateTimeField(
        auto_now_add=True,
    )
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    
class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        INVESTMENT = "investment", "Investment"
        ROI = "roi", "Investment Profit"
        REFERRAL = "referral", "Referral Bonus"
        ADJUSTMENT = "adjustment", "Admin Adjustment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    balance_before = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    balance_after = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    reference = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference}"
    
    
class PaymentMethod(models.Model):

    class MethodType(models.TextChoices):
        CRYPTO = "crypto", "Crypto"
        BANK = "bank", "Bank Transfer"

    name = models.CharField(max_length=100)

    method_type = models.CharField(
        max_length=20,
        choices=MethodType.choices,
    )

    account_name = models.CharField(
        max_length=150,
        blank=True,
    )

    account_number = models.CharField(
        max_length=100,
        blank=True,
    )

    bank_name = models.CharField(
        max_length=150,
        blank=True,
    )

    wallet_address = models.TextField(
        blank=True,
    )

    qr_code = models.ImageField(
        upload_to="payment_qr/",
        blank=True,
        null=True,
    )

    instructions = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Deposit(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposits",
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="deposits",
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    transaction_reference = models.CharField(
        max_length=150,
        blank=True,
    )

    proof = models.ImageField(
        upload_to="deposit_proofs/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_deposits",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejection_reason = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]