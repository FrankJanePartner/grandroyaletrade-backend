from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from finance.models import (
    Wallet,
    Investment,
    Transaction,
)

from finance.utils import generate_investment_reference


class InvestmentService:
    """
    Handles creation of investments.

    Responsibilities:
    - Validate wallet
    - Validate investment plan
    - Lock wallet funds
    - Create investment
    - Create investment transaction
    """

    @staticmethod
    @transaction.atomic
    def create_investment(user, plan, amount):
        """
        Creates an investment and locks the user's funds.
        """

        amount = Decimal(amount)

        # Lock wallet row to prevent double spending
        wallet = Wallet.objects.select_for_update().get(user=user)

        # ------------------------
        # Validate investment plan
        # ------------------------

        if not plan.is_active:
            raise ValidationError("This investment plan is not active.")

        if amount < plan.minimum_amount:
            raise ValidationError(
                f"Minimum investment amount is {plan.minimum_amount}."
            )

        if amount > plan.maximum_amount:
            raise ValidationError(
                f"Maximum investment amount is {plan.maximum_amount}."
            )

        # ------------------------
        # Validate wallet balance
        # ------------------------

        if wallet.available_balance < amount:
            raise ValidationError("Insufficient wallet balance.")

        # ------------------------
        # Calculate returns
        # ------------------------

        expected_profit = (
            amount * plan.roi_percentage
        ) / Decimal("100")

        total_return = amount + expected_profit

        # ------------------------
        # Lock funds
        # ------------------------

        balance_before = wallet.available_balance

        wallet.available_balance -= amount
        wallet.locked_balance += amount

        wallet.save(
            update_fields=[
                "available_balance",
                "locked_balance",
            ]
        )

        # ------------------------
        # Dates
        # ------------------------

        now = timezone.now()

        end_date = now + timedelta(days=plan.duration_days)

        next_roi_at = now + timedelta(days=1)

        # ------------------------
        # Create investment
        # ------------------------

        investment = Investment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            roi_percentage=plan.roi_percentage,
            expected_profit=expected_profit,
            total_return=total_return,
            earned_profit=Decimal("0.00"),
            status=Investment.Status.ACTIVE,
            start_date=now,
            end_date=end_date,
            last_roi_at=None,
            next_roi_at=next_roi_at,
        )

        # ------------------------
        # Create transaction
        # ------------------------

        Transaction.objects.create(
            user=user,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.INVESTMENT,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.available_balance,
            reference=generate_investment_reference(),
            description=f"Investment in {plan.name}",
        )

        return investment