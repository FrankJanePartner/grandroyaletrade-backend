from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Plan, Deposit, Withdrawal, Investment, Transaction, WalletAddresses
from .serializers import (
    PlanSerializer, DepositSerializer, WithdrawalSerializer,
    InvestmentSerializer, TransactionSerializer, WalletAddressesSerializer,
    CreateDepositSerializer, CreateWithdrawalSerializer, CreateInvestmentSerializer
)


class GetPlansView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        plans = Plan.objects.all()
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class GetWalletAddressesView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        wallet = WalletAddresses.objects.first()
        if not wallet:
            return Response({'btc': '', 'eth': '', 'usdt': ''})
        serializer = WalletAddressesSerializer(wallet)
        return Response(serializer.data)


class GetDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Calculate balance
        approved_deposits = Deposit.objects.filter(
            user=user, status='approved'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        active_investments = Investment.objects.filter(
            user=user, status='active'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        approved_withdrawals = Withdrawal.objects.filter(
            user=user, status='approved'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        profit_transactions = Transaction.objects.filter(
            user=user, type='profit', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        balance = approved_deposits + profit_transactions - active_investments - approved_withdrawals
        
        # Get referred users and calculate referral bonus
        from apps.users.models import Profile
        referred_profiles = Profile.objects.filter(referred_by=user.profile)
        referred_users = []
        referral_bonus = Decimal('0')
        
        for profile in referred_profiles:
            referred_user = profile.user
            referred_users.append({
                'id': str(referred_user.id),
                'firstName': referred_user.first_name,
                'lastName': referred_user.last_name,
                'createdAt': referred_user.date_joined.isoformat(),
            })
            
            # Calculate 5% referral bonus from their deposits
            user_approved_deposits = Deposit.objects.filter(
                user=referred_user, status='approved'
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            referral_bonus += user_approved_deposits * Decimal('0.05')
        
        return Response({
            'balance': str(balance),
            'totalInvested': str(active_investments),
            'totalProfit': str(profit_transactions),
            'totalWithdrawn': str(approved_withdrawals),
            'referralBonus': str(referral_bonus),
            'referredUsers': referred_users,
        })


class CreateDepositView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateDepositSerializer(data=request.data)
        if serializer.is_valid():
            deposit = Deposit.objects.create(
                user=request.user,
                amount=serializer.validated_data['amount'],
                method=serializer.validated_data['method'],
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                type='deposit',
                amount=deposit.amount,
                status='pending',
                reference=deposit.id,
            )
            
            return Response(DepositSerializer(deposit).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateWithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            withdrawal = Withdrawal.objects.create(
                user=request.user,
                amount=serializer.validated_data['amount'],
                destination=serializer.validated_data['destination'],
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                type='withdrawal',
                amount=withdrawal.amount,
                status='pending',
                reference=withdrawal.id,
            )
            
            return Response(WithdrawalSerializer(withdrawal).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateInvestmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateInvestmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
            except Plan.DoesNotExist:
                return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
            
            amount = serializer.validated_data['amount']
            expected_profit = amount * plan.roi / Decimal('100')
            
            investment = Investment.objects.create(
                user=request.user,
                plan=plan,
                amount=amount,
                expected_profit=expected_profit,
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                type='investment',
                amount=amount,
                status='approved',
                reference=investment.id,
            )
            
            return Response(InvestmentSerializer(investment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMyTransactionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class GetMyData(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get KYC
        kyc = None
        try:
            from apps.kyc.models import KYC
            kyc_obj = KYC.objects.get(user=user)
            from apps.kyc.serializers import KYCSerializer
            kyc = KYCSerializer(kyc_obj).data
        except:
            pass
        
        # Get investments, deposits, withdrawals, transactions
        investments = Investment.objects.filter(user=user)
        deposits = Deposit.objects.filter(user=user)
        withdrawals = Withdrawal.objects.filter(user=user)
        transactions = Transaction.objects.filter(user=user)
        
        return Response({
            'kyc': kyc,
            'investments': InvestmentSerializer(investments, many=True).data,
            'deposits': DepositSerializer(deposits, many=True).data,
            'withdrawals': WithdrawalSerializer(withdrawals, many=True).data,
            'transactions': TransactionSerializer(transactions, many=True).data,
        })
