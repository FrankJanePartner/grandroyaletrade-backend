from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from .models import Wallet, Investment, Transaction, Deposit, Withdrawal

from decimal import Decimal

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from finance.models import (
    Deposit,
    Wallet,
    Transaction,
)

from finance.utils import create_transaction


@receiver(pre_save, sender=Deposit)
def update_wallet_after_deposit(sender, instance, **kwargs):

    if not instance.pk:
        return

    previous = Deposit.objects.get(pk=instance.pk)

    # Only react when status changes
    if previous.status == instance.status:
        return

    wallet = instance.user.wallet

    # Pending -> Approved
    if (
        previous.status == Deposit.Status.PENDING
        and instance.status == Deposit.Status.APPROVED
    ):

        balance_before = wallet.available_balance

        wallet.available_balance += instance.amount
        wallet.save(update_fields=["available_balance"])

        create_transaction(
            wallet=wallet,
            user=instance.user,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=instance.amount,
            status=Transaction.Status.COMPLETED,
            reference=instance.transaction_reference,
            description="Deposit Approved",
            balance_before=balance_before,
            balance_after=wallet.available_balance,
        )

    # Pending -> Rejected
    elif (
        previous.status == Deposit.Status.PENDING
        and instance.status == Deposit.Status.REJECTED
    ):

        create_transaction(
            wallet=wallet,
            user=instance.user,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=instance.amount,
            status=Transaction.Status.FAILED,
            reference=instance.transaction_reference,
            description="Deposit Rejected",
            balance_before=wallet.available_balance,
            balance_after=wallet.available_balance,
        )
        
@receiver(pre_save, sender=Withdrawal)
def update_wallet_after_withdrawal(sender, instance, **kwargs):

    if not instance.pk:
        return

    previous = Withdrawal.objects.get(pk=instance.pk)

    if previous.status == instance.status:
        return

    wallet = instance.wallet

    # Approved
    if (
        previous.status == Withdrawal.Status.PENDING
        and instance.status == Withdrawal.Status.APPROVED
    ):

        before = wallet.available_balance

        wallet.available_balance -= instance.amount
        wallet.save(update_fields=["available_balance"])

        create_transaction(
            wallet=wallet,
            user=instance.user,
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            amount=instance.amount,
            status=Transaction.Status.COMPLETED,
            reference=instance.reference,
            description="Withdrawal Approved",
            balance_before=before,
            balance_after=wallet.available_balance,
        )

    # Rejected
    elif (
        previous.status == Withdrawal.Status.PENDING
        and instance.status == Withdrawal.Status.REJECTED
    ):

        create_transaction(
            wallet=wallet,
            user=instance.user,
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            amount=instance.amount,
            status=Transaction.Status.FAILED,
            reference=instance.reference,
            description="Withdrawal Rejected",
            balance_before=wallet.available_balance,
            balance_after=wallet.available_balance,
        )
        
        
@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        
