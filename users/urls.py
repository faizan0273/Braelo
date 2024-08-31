# users/urls.py

from django.urls import path
from . import views

from .views import (
    SignUpWithEmailView,
    LoginWithEmailView,
    SignUpWithPhone,
)

urlpatterns = [
    # Login end points
    path('login/email', LoginWithEmailView.as_view(), name='login_with_email'),
    # Sign up endpoints
    path(
        'signup/email', SignUpWithEmailView.as_view(), name='sign_up_with_email'
    ),
    path('signup/phone', SignUpWithPhone.as_view(), name='sign_up_with_phone'),
    path('verify-jwt/', views.verify_jwt, name='verify-jwt'),
    path('verify-me/', views.verify_me, name='verify-jwt'),
]
