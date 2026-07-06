import uuid


def generate_transaction_reference():
    return f"TRX-{uuid.uuid4().hex[:12].upper()}"


def generate_withdrawal_reference():
    return f"WTH-{uuid.uuid4().hex[:12].upper()}"


def generate_deposit_reference():
    return f"DEP-{uuid.uuid4().hex[:12].upper()}"


def generate_investment_reference():
    return f"INV-{uuid.uuid4().hex[:12].upper()}"
