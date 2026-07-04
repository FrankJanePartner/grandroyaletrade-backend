from django.contrib import admin
from .models import Wallet, InvestmentPlan, Investment


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