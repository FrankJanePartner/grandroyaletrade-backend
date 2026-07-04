from django.shortcuts import get_object_or_404

from .models import (
    Deposit,
    PaymentMethod,
)


class DepositSelector:

    @staticmethod
    def payment_methods():

        return PaymentMethod.objects.filter(
            is_active=True
        )


    @staticmethod
    def user_deposits(user):

        return Deposit.objects.filter(
            user=user
        ).select_related(
            "payment_method"
        )


    @staticmethod
    def deposit(user, deposit_id):

        return get_object_or_404(
            Deposit.objects.select_related(
                "payment_method"
            ),
            pk=deposit_id,
            user=user,
        )


    @staticmethod
    def admin_deposit(deposit_id):

        return get_object_or_404(
            Deposit.objects.select_related(
                "user",
                "payment_method",
            ),
            pk=deposit_id,
        )
