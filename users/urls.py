# users/urls.py

from django.urls import path
from . import views

from .views import (
    SignUpWithEmailView,
    LoginWithEmailView,
    SignUpWithPhone,
    GoogleCallbackView,
)

urlpatterns = [
    # Testing
    path('', views.sign_in, name='sign_in'),
    # Login end points
    path('login/email', LoginWithEmailView.as_view(), name='login_with_email'),
    path(
        'login/google', GoogleCallbackView.as_view(), name='login_with_google'
    ),
    # Sign up endpoints
    path(
        'signup/email', SignUpWithEmailView.as_view(), name='sign_up_with_email'
    ),
    path(
        'signup/google',
        GoogleCallbackView.as_view(),
        name='sign_up_with_google',
    ),
    path('signup/phone', SignUpWithPhone.as_view(), name='sign_up_with_phone'),
]
