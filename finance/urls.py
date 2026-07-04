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
        "wallet/",
        WalletAPIView.as_view(),
        name="wallet",
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