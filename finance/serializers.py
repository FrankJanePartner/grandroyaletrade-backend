from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Wallet,
    InvestmentPlan,
    Investment,
    Deposit,
    PaymentMethod,
    Withdrawal,
)


class WalletSerializer(serializers.ModelSerializer):

    total_balance = serializers.ReadOnlyField()

    class Meta:
        model = Wallet
        fields = (
            "id",
            "available_balance",
            "locked_balance",
            "total_profit",
            "total_balance",
            "currency",
        )


class InvestmentPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentPlan
        fields = (
            "id",
            "name",
            "description",
            "minimum_amount",
            "maximum_amount",
            "roi_percentage",
            "duration_days",
            "is_active",
        )


class InvestmentSerializer(serializers.ModelSerializer):

    plan_name = serializers.ReadOnlyField(
        source="plan.name"
    )

    class Meta:
        model = Investment
        fields = (
            "id",
            "plan",
            "plan_name",
            "amount",
            "expected_profit",
            "total_return",
            "status",
            "start_date",
            "end_date",
        )


class CreateInvestmentSerializer(serializers.Serializer):

    plan = serializers.PrimaryKeyRelatedField(
        queryset=InvestmentPlan.objects.filter(
            is_active=True
        )
    )

    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    def validate(self, attrs):

        user = self.context["request"].user

        wallet, _ = Wallet.objects.get_or_create(user=user)

        plan = attrs["plan"]

        amount = attrs["amount"]

        if amount <= 0:
            raise serializers.ValidationError(
                {
                    "amount":
                    "Investment amount must be greater than zero."
                }
            )

        if amount < plan.minimum_amount:
            raise serializers.ValidationError(
                {
                    "amount":
                    f"Minimum investment is {plan.minimum_amount}."
                }
            )

        if amount > plan.maximum_amount:
            raise serializers.ValidationError(
                {
                    "amount":
                    f"Maximum investment is {plan.maximum_amount}."
                }
            )

        if wallet.available_balance < amount:
            raise serializers.ValidationError(
                {
                    "amount":
                    "Insufficient wallet balance."
                }
            )

        return attrs


class PaymentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = (
            "id",
            "name",
            "symbol",
            "network",
            "wallet_address",
            "minimum_deposit",
            "instructions",
            "is_active",
        )


class DepositSerializer(serializers.ModelSerializer):

    payment_method_name = serializers.ReadOnlyField(
        source="payment_method.name"
    )

    class Meta:
        model = Deposit
        fields = (
            "id",
            "payment_method",
            "payment_method_name",
            "currency",
            "network",
            "amount",
            "transaction_hash",
            "transaction_reference",
            "proof",
            "status",
            "created_at",
        )


class DepositCreateSerializer(serializers.Serializer):

    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(is_active=True)
    )

    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    proof = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )
        return value

    def validate(self, attrs):
        payment_method = attrs["payment_method"]
        amount = attrs["amount"]

        if not payment_method.is_active:
            raise serializers.ValidationError(
                {
                    "payment_method":
                    "This payment method is unavailable."
                }
            )

        if amount < payment_method.minimum_deposit:
            raise serializers.ValidationError(
                {
                    "amount":
                    f"Minimum deposit is {payment_method.minimum_deposit}."
                }
            )

        return attrs


class CreateDepositSerializer(serializers.Serializer):
    """Alias kept for backward compatibility."""

    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(
            is_active=True
        )
    )

    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    proof = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )
        return value


class RejectDepositSerializer(serializers.Serializer):
    reason = serializers.CharField()


class WithdrawalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Withdrawal

        fields = "__all__"

        read_only_fields = (
            "id",
            "user",
            "wallet",
            "status",
            "reference",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        )

    def validate_amount(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Withdrawal amount must be greater than zero."
            )

        return value