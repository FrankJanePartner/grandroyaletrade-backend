from decimal import Decimal
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    Investment,
    Deposit,
    Wallet,
    Transaction,
)


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
    


class DepositService:

    @staticmethod
    def create_deposit(
        *,
        user,
        payment_method,
        amount,
        transaction_reference="",
        proof=None,
    ):

        return Deposit.objects.create(
            user=user,
            payment_method=payment_method,
            amount=amount,
            transaction_reference=transaction_reference,
            proof=proof,
        )
        

    @staticmethod
    @transaction.atomic
    def approve_deposit(
        *,
        deposit,
        approved_by,
    ):

        if deposit.status != Deposit.Status.PENDING:
            raise ValueError(
                "Deposit has already been processed."
            )

        wallet = Wallet.objects.select_for_update().get(
            user=deposit.user
        )

        before = wallet.available_balance

        wallet.available_balance += deposit.amount

        wallet.save(
            update_fields=["available_balance"]
        )

        deposit.status = Deposit.Status.APPROVED

        deposit.approved_by = approved_by

        deposit.approved_at = timezone.now()

        deposit.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_at",
            ]
        )

        Transaction.objects.create(
            user=deposit.user,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=deposit.amount,
            balance_before=before,
            balance_after=wallet.available_balance,
            reference=f"DEP-{deposit.pk}",
            description="Wallet Deposit",
        )

        return deposit


    @staticmethod
    def reject_deposit(
        *,
        deposit,
        reason,
    ):

        if deposit.status != Deposit.Status.PENDING:
            raise ValueError(
                "Deposit has already been processed."
            )

        deposit.status = Deposit.Status.REJECTED

        deposit.rejection_reason = reason

        deposit.save(
            update_fields=[
                "status",
                "rejection_reason",
            ]
        )

        return deposit