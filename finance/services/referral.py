from decimal import Decimal
import uuid

from django.db import transaction

from finance.models import Transaction, Wallet
from finance.services.transaction import TransactionService


class ReferralService:
    REFERRAL_BONUS_PERCENTAGE = Decimal("0.05")  # 5% bonus on deposits

    @staticmethod
    @transaction.atomic
    def process_referral_bonus(deposit):
        """
        Calculates and credits the referral bonus to the referrer (if any)
        when a deposit is successfully approved.
        """
        user = deposit.user
        
        if not user.referred_by:
            return None
            
        referrer = user.referred_by
        
        # Calculate bonus amount
        bonus_amount = deposit.amount * ReferralService.REFERRAL_BONUS_PERCENTAGE
        bonus_amount = bonus_amount.quantize(Decimal("0.01"))
        
        if bonus_amount <= 0:
            return None
            
        wallet, _ = Wallet.objects.get_or_create(user=referrer)
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        
        balance_before = wallet.available_balance
        
        # Credit the referrer's wallet and total profit
        wallet.available_balance += bonus_amount
        wallet.total_profit += bonus_amount
        wallet.save(update_fields=["available_balance", "total_profit", "updated_at"])
        
        # Create a referral transaction
        tx = TransactionService.create_transaction(
            user=referrer,
            wallet=wallet,
            transaction_type=Transaction.TransactionType.REFERRAL,
            amount=bonus_amount,
            balance_before=balance_before,
            balance_after=wallet.available_balance,
            reference=f"REF-{uuid.uuid4().hex[:12]}",
            description=f"Referral bonus from {user.first_name} {user.last_name}'s deposit",
        )
        
        return tx
