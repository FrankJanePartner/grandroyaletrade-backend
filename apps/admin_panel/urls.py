from django.urls import path
from .views import (
    ListUsersView, ListAllTransactionsView, SetKycStatusView,
    SetDepositStatusView, SetWithdrawalStatusView, UpsertPlanView,
    DeletePlanView, UpdateWalletsView, ListMessagesView,
    SetMessageStatusView, DeleteMessageView, GetAdminDataView
)

urlpatterns = [
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('transactions/', ListAllTransactionsView.as_view(), name='list_transactions'),
    path('kyc/status/', SetKycStatusView.as_view(), name='set_kyc_status'),
    path('deposits/status/', SetDepositStatusView.as_view(), name='set_deposit_status'),
    path('withdrawals/status/', SetWithdrawalStatusView.as_view(), name='set_withdrawal_status'),
    path('plans/upsert/', UpsertPlanView.as_view(), name='upsert_plan'),
    path('plans/delete/', DeletePlanView.as_view(), name='delete_plan'),
    path('wallets/update/', UpdateWalletsView.as_view(), name='update_wallets'),
    path('messages/', ListMessagesView.as_view(), name='list_messages'),
    path('messages/status/', SetMessageStatusView.as_view(), name='set_message_status'),
    path('messages/delete/', DeleteMessageView.as_view(), name='delete_message'),
    path('data/', GetAdminDataView.as_view(), name='get_admin_data'),
]
