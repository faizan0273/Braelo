'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
End points registry file.
---------------------------------------------------
'''

from . import views
from django.urls import path
from .api.user_interest import InterestListCreateView
from .api import (
    LoginWithEmail,
    VerifyOTP,
    GoogleCallback,
    SignUpWithEmail,
    SignUpWithPhone,
    TokenRefresh,
    ForgotPassword,
    ChangePassword,
    Logout,
    CreatePassword,
)


# todo import from separate files.

urlpatterns = [
    # Testing
    path('', views.sign_in, name='sign_in'),
    # Login end points
    path('login/email', LoginWithEmail.as_view(), name='email_login'),
    path('verifyotp', VerifyOTP.as_view(), name='phone_login'),
    path('login/google', GoogleCallback.as_view(), name='google_login'),
    # Sign up endpoints
    path('signup/email', SignUpWithEmail.as_view(), name='email_signup'),
    path('signup/phone', SignUpWithPhone.as_view(), name='phone_signup'),
    path('signup/google', GoogleCallback.as_view(), name='google_signup'),
    # Refresh token
    path('token/refresh', TokenRefresh.as_view(), name='token_refresh'),
    # Forgot password
    path('forgot/password', ForgotPassword.as_view(), name='forgot_password'),
    # Change password
    path('change/password', ChangePassword.as_view(), name='change_password'),
    # Create new password
    path('new/password', CreatePassword.as_view(), name='create_password'),
    # Logout
    path('api/logout', Logout.as_view(), name='logout'),
    path('interests', InterestListCreateView.as_view(), name='interest'),
]
