from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    Wallet,
    InvestmentPlan,
    Investment,
    Deposit,
    PaymentMethod,
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
    DepositSerializer,
)
from .services.investment import InvestmentService
from .services.deposit import DepositService


class WalletAPIView(generics.RetrieveAPIView):

    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


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


class CreateInvestmentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = CreateInvestmentSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        inv = InvestmentService.create_investment(
            user=request.user,
            plan=serializer.validated_data["plan"],
            amount=serializer.validated_data["amount"],
        )

        return Response(
            InvestmentSerializer(inv).data,
            status=status.HTTP_201_CREATED,
        )


class MyDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        wallet, _ = Wallet.objects.get_or_create(user=request.user)

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

    permission_classes = [AllowAny]

    def get(self, request):

        methods = PaymentMethod.objects.filter(is_active=True)

        serializer = PaymentMethodSerializer(
            methods,
            many=True,
        )

        return Response(serializer.data)


class DepositListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        deposits = Deposit.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = DepositSerializer(
            deposits,
            many=True,
        )

        return Response(serializer.data)


class DepositDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            deposit = Deposit.objects.get(pk=pk, user=request.user)
        except Deposit.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DepositSerializer(deposit)

        return Response(serializer.data)


class CreateDepositAPIView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):

        serializer = DepositCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        dep = DepositService.create_deposit(
            user=request.user,
            payment_method=serializer.validated_data["payment_method"],
            amount=serializer.validated_data["amount"],
            proof=serializer.validated_data.get("proof"),
        )

        return Response(
            {
                "success": True,
                "message": "Deposit submitted successfully. Please await admin approval.",
                "deposit": DepositSerializer(dep).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MyDepositsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        deposits = Deposit.objects.filter(
            user=request.user
        ).order_by("-created_at")

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

        try:
            dep = Deposit.objects.get(pk=pk)
        except Deposit.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        DepositService.reject_deposit(
            deposit=dep,
            reason=serializer.validated_data["reason"],
        )

        return Response({
            "success": True,
            "message": "Deposit rejected."
        })


class ApproveDepositAPIView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        try:
            dep = Deposit.objects.get(pk=pk)
        except Deposit.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        DepositService.approve_deposit(
            deposit=dep,
            approved_by=request.user,
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