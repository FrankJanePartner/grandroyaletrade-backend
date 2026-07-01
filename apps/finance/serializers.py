from rest_framework import serializers
from .models import Plan, Deposit, Withdrawal, Investment, Transaction, WalletAddresses
from django.db.models import Sum, Q
from decimal import Decimal


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'min_amount', 'max_amount', 'roi', 'duration_days']


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['id', 'amount', 'method', 'status', 'created_at']


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'amount', 'destination', 'status', 'created_at']


class InvestmentSerializer(serializers.ModelSerializer):
    plan_id = serializers.CharField(source='plan.id', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta:
        model = Investment
        fields = ['id', 'plan_id', 'plan_name', 'amount', 'expected_profit', 'status', 'start_date', 'end_date']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'status', 'reference', 'created_at']


class WalletAddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletAddresses
        fields = ['btc', 'eth', 'usdt']


class CreateDepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    method = serializers.ChoiceField(choices=['crypto', 'bank'])


class CreateWithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    destination = serializers.CharField(max_length=500)


class CreateInvestmentSerializer(serializers.Serializer):
    plan_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class DashboardSummarySerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_invested = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_withdrawn = serializers.DecimalField(max_digits=15, decimal_places=2)
    referral_bonus = serializers.DecimalField(max_digits=15, decimal_places=2)
    referred_users = serializers.ListField()
