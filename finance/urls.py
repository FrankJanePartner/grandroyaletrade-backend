from django.urls import path

from .views import (
    WalletAPIView,
    InvestmentPlanListAPIView,
    InvestmentListAPIView,
    CreateInvestmentAPIView,
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

]