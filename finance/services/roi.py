from datetime import timedelta
from decimal import Decimal
import uuid

from django.db import transaction
from django.utils import timezone

from finance.models import (
    Investment,
    InvestmentStatus,
    Transaction,
)

from finance.services.transaction import TransactionService


class ROIService:

    @staticmethod
    def process_due_investments():

        investments = (
            Investment.objects
            .select_related("user", "user__wallet", "plan")
            .filter(
                status=InvestmentStatus.ACTIVE,
                next_roi_at__lte=timezone.now(),
            )
        )

        processed = 0

        for investment in investments:
            ROIService.process_investment(investment)
            processed += 1

        return processed

    @staticmethod
    @transaction.atomic
    def process_investment(investment):

        wallet = investment.user.wallet

        now = timezone.now()

        if investment.plan.roi_frequency == "daily":
            roi_amount = (
                investment.expected_profit /
                investment.plan.duration_days
            )

        elif investment.plan.roi_frequency == "weekly":
            roi_amount = (
                investment.expected_profit /
                max(1, investment.plan.duration_days // 7)
            )

        elif investment.plan.roi_frequency == "monthly":
            roi_amount = (
                investment.expected_profit /
                max(1, investment.plan.duration_days // 30)
            )

        else:
            roi_amount = Decimal("0.00")

        roi_amount = roi_amount.quantize(Decimal("0.01"))

        before = wallet.available_balance

        wallet.available_balance += roi_amount
        wallet.total_profit += roi_amount

        wallet.save(update_fields=[
            "available_balance",
            "total_profit",
            "updated_at",
        ])

        investment.earned_profit += roi_amount
        investment.total_payouts += 1
        investment.last_roi_at = now

        if investment.plan.roi_frequency == "daily":
            investment.next_roi_at += timedelta(days=1)

        elif investment.plan.roi_frequency == "weekly":
            investment.next_roi_at += timedelta(days=7)

        elif investment.plan.roi_frequency == "monthly":
            investment.next_roi_at += timedelta(days=30)

        investment.save(update_fields=[
            "earned_profit",
            "total_payouts",
            "last_roi_at",
            "next_roi_at",
            "updated_at",
        ])

        Transaction.objects.create(
            user=investment.user,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.ROI,
            amount=roi_amount,
            balance_before=before,
            balance_after=wallet.available_balance,
            remaining_profit=(
                investment.expected_profit -
                investment.earned_profit
            ),
            status=Transaction.Status.COMPLETED,
            reference=f"ROI-{uuid.uuid4().hex[:12]}",
            description=f"ROI payout for {investment.plan.name}",
        )

        if (
            investment.earned_profit >= investment.expected_profit
            or now >= investment.end_date
        ):
            ROIService.complete_investment(investment)

    @staticmethod
    @transaction.atomic
    def complete_investment(investment):

        wallet = investment.user.wallet

        before = wallet.available_balance

        wallet.locked_balance -= investment.amount
        wallet.available_balance += investment.amount

        wallet.save(update_fields=[
            "locked_balance",
            "available_balance",
            "updated_at",
        ])

        investment.status = InvestmentStatus.COMPLETED
        investment.completed_at = timezone.now()

        investment.save(update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ])

        Transaction.objects.create(
            user=investment.user,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.INVESTMENT,
            amount=investment.amount,
            balance_before=before,
            balance_after=wallet.available_balance,
            remaining_profit=Decimal("0.00"),
            status=Transaction.Status.COMPLETED,
            reference=f"INV-END-{uuid.uuid4().hex[:12]}",
            description="Investment completed. Principal returned.",
        )


def process_all_investments():
    return ROIService.process_due_investments()