# users/urls.py

from django.urls import path
from . import views

from .views import (
    SignUpWithEmail,
    LoginWithEmail,
    SignUpWithPhone,
    GoogleCallback,
    LoginWithPhone,
    TokenRefresh,
    ResetPassword,
    ForgotPassword,
    ChangePassword,
    Logout,
    # InterestListCreateView,
    # InterestDetailView,
)

# todo import from separate files.

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
    # Refresh token
    path('token/refresh', TokenRefresh.as_view(), name='token_refresh'),
    # Reset password
    path('reset/password', ResetPassword.as_view(), name='reset_password'),
    # Forgot password
    path('forgot/password', ForgotPassword.as_view(), name='forgot_password'),
    # Change password
    path('change/password', ChangePassword.as_view(), name='change_password'),
    # Logout
    path('api/logout/', Logout.as_view(), name='logout'),
    # path(
    #     'interests/',
    #     InterestListCreateView.as_view(),
    #     name='interest-list-create',
    # ),
    # path(
    #     'interests/<str:id>/',
    #     InterestDetailView.as_view(),
    #     name='interest-detail',
    # ),
]
