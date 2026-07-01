from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from apps.users.models import UserRole
from apps.finance.models import Plan, Deposit, Withdrawal, Investment, Transaction, WalletAddresses
from apps.finance.serializers import (
    PlanSerializer, DepositSerializer, WithdrawalSerializer,
    InvestmentSerializer, TransactionSerializer, WalletAddressesSerializer
)
from apps.kyc.models import KYC, ContactMessage
from apps.kyc.serializers import KYCSerializer, ContactMessageSerializer
from apps.users.serializers import UserSerializer
from django.db.models import Sum
from decimal import Decimal


def is_admin(user):
    """Check if user is admin"""
    try:
        return user.role_profile.role == 'admin'
    except:
        return False


class ListUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ListAllTransactionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        transactions = Transaction.objects.all().order_by('-created_at')
        from apps.finance.serializers import TransactionSerializer
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class SetKycStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        kyc_id = request.data.get('kyc_id')
        status_update = request.data.get('status')
        
        try:
            kyc = KYC.objects.get(id=kyc_id)
            kyc.status = status_update
            kyc.save()
            return Response(KYCSerializer(kyc).data)
        except KYC.DoesNotExist:
            return Response({'error': 'KYC not found'}, status=status.HTTP_404_NOT_FOUND)


class SetDepositStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        deposit_id = request.data.get('deposit_id')
        status_update = request.data.get('status')
        
        try:
            deposit = Deposit.objects.get(id=deposit_id)
            deposit.status = status_update
            deposit.save()
            
            # Update related transaction
            Transaction.objects.filter(reference=deposit_id).update(status=status_update)
            
            # Award 5% referral bonus if approved
            if status_update == 'approved':
                user_profile = deposit.user.profile
                if user_profile.referred_by:
                    referrer = user_profile.referred_by.user
                    bonus_amount = deposit.amount * Decimal('0.05')
                    Transaction.objects.create(
                        user=referrer,
                        type='profit',
                        amount=bonus_amount,
                        status='completed',
                        reference=deposit.id,
                    )
            
            return Response(DepositSerializer(deposit).data)
        except Deposit.DoesNotExist:
            return Response({'error': 'Deposit not found'}, status=status.HTTP_404_NOT_FOUND)


class SetWithdrawalStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        withdrawal_id = request.data.get('withdrawal_id')
        status_update = request.data.get('status')
        
        try:
            withdrawal = Withdrawal.objects.get(id=withdrawal_id)
            withdrawal.status = status_update
            withdrawal.save()
            
            # Update related transaction
            Transaction.objects.filter(reference=withdrawal_id).update(status=status_update)
            
            return Response(WithdrawalSerializer(withdrawal).data)
        except Withdrawal.DoesNotExist:
            return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)


class UpsertPlanView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        plan_id = request.data.get('id')
        
        plan_data = {
            'name': request.data.get('name'),
            'description': request.data.get('description', ''),
            'min_amount': request.data.get('min_amount'),
            'max_amount': request.data.get('max_amount'),
            'roi': request.data.get('roi'),
            'duration_days': request.data.get('duration_days'),
        }
        
        if plan_id:
            try:
                plan = Plan.objects.get(id=plan_id)
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
            except Plan.DoesNotExist:
                return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            plan = Plan.objects.create(**plan_data)
        
        return Response(PlanSerializer(plan).data)


class DeletePlanView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        plan_id = request.data.get('plan_id')
        
        try:
            plan = Plan.objects.get(id=plan_id)
            plan.delete()
            return Response({'ok': True})
        except Plan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateWalletsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        wallet, _ = WalletAddresses.objects.get_or_create(pk=1)
        
        if 'btc' in request.data:
            wallet.btc = request.data['btc']
        if 'eth' in request.data:
            wallet.eth = request.data['eth']
        if 'usdt' in request.data:
            wallet.usdt = request.data['usdt']
        
        wallet.save()
        return Response(WalletAddressesSerializer(wallet).data)


class ListMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        messages = ContactMessage.objects.all().order_by('-created_at')
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)


class SetMessageStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        message_id = request.data.get('message_id')
        status_update = request.data.get('status')
        
        try:
            message = ContactMessage.objects.get(id=message_id)
            message.status = status_update
            message.save()
            return Response(ContactMessageSerializer(message).data)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)


class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        message_id = request.data.get('message_id')
        
        try:
            message = ContactMessage.objects.get(id=message_id)
            message.delete()
            return Response({'ok': True})
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)


class GetAdminDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not is_admin(request.user):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        roles = UserRole.objects.all()
        kyc_list = KYC.objects.all()
        deposits = Deposit.objects.all()
        withdrawals = Withdrawal.objects.all()
        investments = Investment.objects.all()
        transactions = Transaction.objects.all()
        messages = ContactMessage.objects.all()
        wallet = WalletAddresses.objects.first()
        plans = Plan.objects.all()
        
        return Response({
            'users': UserSerializer(users, many=True).data,
            'roles': [{'user_id': str(r.user.id), 'role': r.role} for r in roles],
            'kyc': KYCSerializer(kyc_list, many=True).data,
            'deposits': DepositSerializer(deposits, many=True).data,
            'withdrawals': WithdrawalSerializer(withdrawals, many=True).data,
            'investments': InvestmentSerializer(investments, many=True).data,
            'transactions': TransactionSerializer(transactions, many=True).data,
            'messages': ContactMessageSerializer(messages, many=True).data,
            'wallets': WalletAddressesSerializer(wallet).data if wallet else {'btc': '', 'eth': '', 'usdt': ''},
            'plans': PlanSerializer(plans, many=True).data,
        })
