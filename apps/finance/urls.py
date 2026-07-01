from django.urls import path
from .views import (
    GetPlansView, GetWalletAddressesView, GetDashboardSummaryView,
    CreateDepositView, CreateWithdrawalView, CreateInvestmentView,
    GetMyTransactionsView, GetMyData
)

urlpatterns = [
    path('plans/', GetPlansView.as_view(), name='get_plans'),
    path('wallets/', GetWalletAddressesView.as_view(), name='get_wallets'),
    path('summary/', GetDashboardSummaryView.as_view(), name='dashboard_summary'),
    path('deposits/create/', CreateDepositView.as_view(), name='create_deposit'),
    path('withdrawals/create/', CreateWithdrawalView.as_view(), name='create_withdrawal'),
    path('investments/create/', CreateInvestmentView.as_view(), name='create_investment'),
    path('transactions/', GetMyTransactionsView.as_view(), name='get_transactions'),
    path('my-data/', GetMyData.as_view(), name='my_data'),
]
