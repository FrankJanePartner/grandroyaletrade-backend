from decimal import Decimal

from django.db import transaction

from ..models import Transaction


class TransactionService:

    @staticmethod
    @transaction.atomic
    def create_transaction(
        *,
        user,
        wallet,
        transaction_type,
        amount,
        balance_before,
        balance_after,
        reference,
        description="",
        status=Transaction.Status.COMPLETED,
    ):

        amount = Decimal(amount)

        return Transaction.objects.create(
            user=user,
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference=reference,
            description=description,
            status=status,
        )