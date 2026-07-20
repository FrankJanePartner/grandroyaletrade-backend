from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from finance.models import Deposit, Wallet, Transaction
from finance.utils import generate_deposit_reference
from finance.services.referral import ReferralService


class DepositService:

    @staticmethod
    def create_deposit(
        *,
        user,
        payment_method,
        amount,
        transaction_reference=None,
        proof=None,
    ):
        if transaction_reference is None:
            transaction_reference = generate_deposit_reference()

        return Deposit.objects.create(
            user=user,
            payment_method=payment_method,
            currency=payment_method.symbol,
            network=payment_method.network,
            amount=amount,
            transaction_hash="",
            transaction_reference=transaction_reference,
            proof=proof,
        )

    @staticmethod
    @transaction.atomic
    def approve_deposit(*, deposit, approved_by):
        if deposit.status != Deposit.Status.PENDING:
            raise ValueError("Deposit has already been processed.")

        wallet, _ = Wallet.objects.get_or_create(user=deposit.user)
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

        before = wallet.available_balance
        wallet.available_balance += deposit.amount
        wallet.save(update_fields=["available_balance"])

        deposit.status = Deposit.Status.APPROVED
        deposit.approved_by = approved_by
        deposit.approved_at = timezone.now()
        deposit.save(update_fields=["status", "approved_by", "approved_at"])

        Transaction.objects.create(
            user=deposit.user,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=deposit.amount,
            balance_before=before,
            balance_after=wallet.available_balance,
            reference=f"DEP-{deposit.pk}-{generate_deposit_reference()}",
            description="Wallet Deposit",
        )

        ReferralService.process_referral_bonus(deposit)

        return deposit

    @staticmethod
    def reject_deposit(*, deposit, reason):
        if deposit.status != Deposit.Status.PENDING:
            raise ValueError("Deposit has already been processed.")

        deposit.status = Deposit.Status.REJECTED
        deposit.rejection_reason = reason
        deposit.save(update_fields=["status", "rejection_reason"])

        return deposit
