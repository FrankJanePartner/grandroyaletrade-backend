
# finance/utils.py

from finance.models import Transaction


def create_transaction(
    *,
    wallet,
    user,
    transaction_type,
    amount,
    status,
    reference,
    description="",
    balance_before,
    balance_after,
):
    return Transaction.objects.create(
        wallet=wallet,
        user=user,
        transaction_type=transaction_type,
        amount=amount,
        status=status,
        reference=reference,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after,
    )
import uuid


def generate_transaction_reference():
    return f"TRX-{uuid.uuid4().hex[:12].upper()}"


def generate_withdrawal_reference():
    return f"WTH-{uuid.uuid4().hex[:12].upper()}"


def generate_deposit_reference():
    return f"DEP-{uuid.uuid4().hex[:12].upper()}"


def generate_investment_reference():
    return f"INV-{uuid.uuid4().hex[:12].upper()}"
