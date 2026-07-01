from django.urls import path
from .views import (
    RegisterView, LoginView, GetProfileView,
    UpdateProfileView, VerifyPasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', GetProfileView.as_view(), name='get_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/verify-password/', VerifyPasswordView.as_view(), name='verify_password'),
]
