from django.urls import path

from .views import (
    WalletAPIView,
    InvestmentPlanListAPIView,
    InvestmentListAPIView,
    CreateInvestmentAPIView,
    MyDataAPIView,
    PaymentMethodListAPIView,
    DepositListAPIView,
    DepositDetailAPIView,
    CreateDepositAPIView,
    ApproveDepositAPIView,
    RejectDepositAPIView,
    MyDepositsAPIView,
    AdminDepositListAPIView,
)


app_name = "finance"
urlpatterns = [

    path(
        "wallets/",
        WalletAPIView.as_view(),
        name="wallets",
    ),

    path(
        "plans/",
        InvestmentPlanListAPIView.as_view(),
        name="plans",
    ),

    path(
        "investments/",
        InvestmentListAPIView.as_view(),
        name="investments",
    ),

    path(
        "investments/create/",
        CreateInvestmentAPIView.as_view(),
        name="create-investment",
    ),
    path(
        "my-data/",
        MyDataAPIView.as_view(),
        name="my-data",
    ),
    path(
        "payment-methods/",
        PaymentMethodListAPIView.as_view(),
        name="payment-method-list",
    ),
    path(
        "deposits/",
        DepositListAPIView.as_view(),
        name="deposit-list",
    ),
    path(
        "deposits/create/",
        CreateDepositAPIView.as_view(),
        name="deposit-create",
    ),
    path(
        "deposits/<int:pk>/",
        DepositDetailAPIView.as_view(),
        name="deposit-detail",
    ),
    path(
        "deposits/<int:pk>/approve/",
        ApproveDepositAPIView.as_view(),
        name="deposit-approve",
    ),
    path(
        "deposits/<int:pk>/reject/",
        RejectDepositAPIView.as_view(),
        name="deposit-reject",
    ),


    path(
        "my-deposits/",
        MyDepositsAPIView.as_view(),
        name="my-deposits",
    ),
]