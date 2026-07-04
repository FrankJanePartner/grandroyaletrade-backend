from decimal import Decimal
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Investment


class InvestmentService:

    @staticmethod
    @transaction.atomic
    def create_investment(
        *,
        user,
        plan,
        amount,
    ):

        wallet = user.wallet

        expected_profit = (
            amount * plan.roi_percentage
        ) / Decimal("100")

        total_return = amount + expected_profit

        wallet.available_balance -= amount
        wallet.locked_balance += amount

        wallet.save()

        investment = Investment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            expected_profit=expected_profit,
            total_return=total_return,
            status="active",
            end_date=timezone.now()
            + timedelta(days=plan.duration_days),
        )

        return investment