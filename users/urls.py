# users/urls.py

from django.urls import path
from . import views

from .views import (
    SignUpWithEmail,
    LoginWithEmail,
    SignUpWithPhone,
    GoogleCallback,
    LoginWithPhone,
)

urlpatterns = [
    # Testing
    path('', views.sign_in, name='sign_in'),
    # Login end points
    path('login/email', LoginWithEmail.as_view(), name='email_login'),
    path('login/phone', LoginWithPhone.as_view(), name='phone_login'),
    path('login/google', GoogleCallback.as_view(), name='google_login'),
    # Sign up endpoints
    path('signup/email', SignUpWithEmail.as_view(), name='email_signup'),
    path('signup/phone', SignUpWithPhone.as_view(), name='phone_signup'),
    path('signup/google', GoogleCallback.as_view(), name='google_signup'),
]
