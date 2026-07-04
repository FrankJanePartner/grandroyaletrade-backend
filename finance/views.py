from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import (
    Wallet,
    InvestmentPlan,
    Investment,
)

from .serializers import (
    WalletSerializer,
    InvestmentPlanSerializer,
    InvestmentSerializer,
    CreateInvestmentSerializer,
)

from .services import InvestmentService


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

        serializer.instance = InvestmentService.create_investment(
            user=self.request.user,
            plan=serializer.validated_data["plan"],
            amount=serializer.validated_data["amount"],
        )

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        investment = InvestmentService.create_investment(
            user=request.user,
            plan=serializer.validated_data["plan"],
            amount=serializer.validated_data["amount"],
        )

        return Response(
            InvestmentSerializer(investment).data
        )