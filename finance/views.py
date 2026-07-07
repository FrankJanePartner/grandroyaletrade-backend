from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from .models import (
    Wallet,
    InvestmentPlan,
    Investment,
    Deposit,
)
from rest_framework.views import APIView
from .serializers import (
    WalletSerializer,
    InvestmentPlanSerializer,
    InvestmentSerializer,
    CreateInvestmentSerializer,
    CreateDepositSerializer,
    PaymentMethodSerializer,
    RejectDepositSerializer,
    DepositCreateSerializer,
)
from .services import investment, deposit



class WalletAPIView(generics.RetrieveAPIView):

    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet


class InvestmentPlanListAPIView(generics.ListAPIView):
    queryset = InvestmentPlan.objects.filter(is_active=True)
    serializer_class = InvestmentPlanSerializer
    permission_classes = [AllowAny]


class InvestmentListAPIView(generics.ListAPIView):

    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class CreateInvestmentAPIView(generics.CreateAPIView):

    serializer_class = CreateInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.instance = investment.create_investment(
            user=self.request.user,
            plan=serializer.validated_data["plan"],
            amount=serializer.validated_data["amount"],
        )

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        investment = investment.create_investment(
            user=request.user,
            plan=serializer.validated_data["plan"],
            amount=serializer.validated_data["amount"],
        )

        return Response(
            InvestmentSerializer(investment).data
        )
        
        

class MyDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        wallet = request.user.wallet

        investments = Investment.objects.filter(
            user=request.user
        ).order_by("-created_at")[:5]

        return Response({
            "wallet": WalletSerializer(wallet).data,
            "active_investments": InvestmentSerializer(
                investments,
                many=True,
            ).data,
            "statistics": {
                "total_invested": wallet.locked_balance,
                "total_profit": wallet.total_profit,
                "wallet_balance": wallet.available_balance,
            },
        })
        
        
class PaymentMethodListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        methods = DepositSelector.payment_methods()

        serializer = PaymentMethodSerializer(
            methods,
            many=True,
        )

        return Response(serializer.data)
    
    
class DepositListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        deposits = DepositSelector.user_deposits(
            request.user
        )

        serializer = DepositSerializer(
            deposits,
            many=True,
        )

        return Response(serializer.data)
    
class DepositDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        deposit = DepositSelector.deposit(
            request.user,
            pk,
        )

        serializer = DepositSerializer(deposit)

        return Response(serializer.data)
    
    
class CreateDepositAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = DepositCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        deposit = deposit.create(
            user=request.user,
            payment_method=serializer.validated_data["payment_method"],
            amount=serializer.validated_data["amount"],
            transaction_hash=serializer.validated_data["transaction_hash"],
            network=serializer.validated_data["network"],
            proof=serializer.validated_data.get("proof"),
        )

        return Response(
            {
                "success": True,
                "message": "Deposit submitted successfully.",
                "deposit": DepositSerializer(deposit).data,
            },
            status=status.HTTP_201_CREATED,
        )
        

class MyDepositsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        deposits = Deposit.objects.filter(
            user=request.user
        )

        serializer = DepositSerializer(
            deposits,
            many=True,
        )

        return Response(serializer.data)


class RejectDepositAPIView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        serializer = RejectDepositSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        deposit = Deposit.objects.get(pk=pk)

        deposit.reject(
            deposit,
            request.user,
            serializer.validated_data["reason"],
        )

        return Response({
            "success": True,
            "message": "Deposit rejected."
        })
        
class ApproveDepositAPIView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        deposit = Deposit.objects.get(pk=pk)

        deposit.approve(
            deposit,
            request.user,
        )

        return Response({
            "success": True,
            "message": "Deposit approved."
        })
        
        
class AdminDepositListAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        deposits = Deposit.objects.select_related(
            "user",
            "payment_method",
        ).order_by("-created_at")

        serializer = DepositSerializer(
            deposits,
            many=True,
        )

        return Response(serializer.data)