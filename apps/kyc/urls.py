from django.urls import path
from .views import (
    SubmitKYCView, GetKYCView, SubmitContactMessageView
)

urlpatterns = [
    path('submit/', SubmitKYCView.as_view(), name='submit_kyc'),
    path('get/', GetKYCView.as_view(), name='get_kyc'),
    path('contact-message/', SubmitContactMessageView.as_view(), name='contact_message'),
]
