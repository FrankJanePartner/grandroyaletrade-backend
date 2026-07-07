from decimal import Decimal
from django.db import transaction
from ..models import Wallet

class WalletService:

    @staticmethod
    @transaction.atomic
    def credit(wallet, amount):
        amount = Decimal(amount)

        before = wallet.available_balance
        wallet.available_balance += amount

        wallet.save(update_fields=[
            "available_balance",
            "updated_at",
        ])

        return before, wallet.available_balance
    
    
    @staticmethod
    @transaction.atomic
    def debit(wallet, amount):
        amount = Decimal(amount)

        if wallet.available_balance < amount:
            raise ValueError("Insufficient wallet balance.")

        before = wallet.available_balance

        wallet.available_balance -= amount

        wallet.save(update_fields=[
            "available_balance",
            "updated_at",
        ])

        return before, wallet.available_balance
    

    @staticmethod
    @transaction.atomic
    def lock(wallet, amount):

        amount = Decimal(amount)

        if wallet.available_balance < amount:

            raise ValueError(
                "Insufficient wallet balance."
            )

        wallet.available_balance -= amount

        wallet.locked_balance += amount

        wallet.save()

        return wallet

    @staticmethod
    @transaction.atomic
    def unlock(wallet, amount):

        amount = Decimal(amount)

        if wallet.locked_balance < amount:

            raise ValueError(
                "Locked balance is too low."
            )

        wallet.locked_balance -= amount

        wallet.available_balance += amount

        wallet.save()

        return wallet
    

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

        return Transaction.objects.create(
            user=user,
            wallet=wallet,
            transaction_type=transaction_type,
            amount=Decimal(amount),
            balance_before=balance_before,
            balance_after=balance_after,
            reference=reference,
            description=description,
            status=status,
        )

    @staticmethod
    @transaction.atomic
    def add_profit(wallet, amount):

        amount = Decimal(amount)

        wallet.available_balance += amount

        wallet.total_profit += amount

        wallet.save()

        return wallet