from django.contrib import admin
from .models import Wallet, InvestmentPlan, Investment, Deposit, PaymentMethod, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "available_balance",
        "locked_balance",
        "total_profit",
    )


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "minimum_amount",
        "maximum_amount",
        "roi_percentage",
        "duration_days",
        "is_active",
    )


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "amount",
        "status",
        "start_date",
        "end_date",
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "symbol",
        "network",
        "is_active",
        "created_at",
    )

    list_filter = (
        "network",
        "is_active",
    )

    search_fields = (
        "name",
        "symbol",
        "network",
        "wallet_address",
    )

    ordering = (
        "name",
    )


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
    )

    search_fields = (
        "user__email",
        "transaction_reference",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "user",
        "transaction_type",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "status",
    )

    search_fields = (
        "reference",
        "user__email",
    )
    
    