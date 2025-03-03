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

from .api.devices import SaveDeviceToken
from .api.user_interest import InterestListCreateView
from .api import (
    LoginWithEmail,
    VerifyOTP,
    SignUpWithEmail,
    LoginAuth,
    TokenRefresh,
    ForgotPassword,
    ChangePassword,
    Logout,
    CreatePassword,
    UpdateProfile,
    UserProfile,
    AboutUser,
    DeactivateUser,
    PublicProfile,
    FlipUserStatus,
    BusinessDashboard,
    BussinessListing,
    FetchBusinesses,
    ScanBusinessQR,
    DeactivateBusiness,
    FetchListings,
    UpdateBusiness,
    Activate_Business,
    FetchSingleBusiness,
    ExploreBusiness,
    BusinessBanner,
)

# todo import from separate files.

urlpatterns = [
    # Testing
    path('', views.sign_in, name='sign_in'),
    # Login end points
    path('login/email', LoginWithEmail.as_view(), name='email_login'),
    path('verifyotp', VerifyOTP.as_view(), name='phone_login'),
    # Sign up endpoints
    path('signup/email', SignUpWithEmail.as_view(), name='email_signup'),
    # Sign_up/Login [Google, Apple, Phone]
    path('login', LoginAuth.as_view(), name='google-apple-phone_login'),
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
    # Update Profile
    path('update/profile', UpdateProfile.as_view(), name='update_profile'),
    path('user/profile', UserProfile.as_view(), name='user_profile'),
    # about user
    path('user/about', AboutUser.as_view(), name='about_user'),
    # Delete
    path('user/delete', DeactivateUser.as_view(), name='delete_user'),
    # Public Profile
    path('public-profile', PublicProfile.as_view(), name='public_profile'),
    # Flip User Status
    path('user/flip-status', FlipUserStatus.as_view(), name='flip_user_status'),
    # Add device Token
    path('device/token', SaveDeviceToken.as_view()),
    # Business Dashboard
    path('business/dashboard', BusinessDashboard.as_view()),
    # Business Lisitng
    path('business', BussinessListing.as_view()),
    # fetch all Business
    path('business/fetch', FetchBusinesses.as_view()),
    # Deactive Business
    path('business/deactivate', DeactivateBusiness.as_view()),
    # Fetch Listings of Business
    path('business/listings', FetchListings.as_view()),
    # Activate business
    path('business/activate', Activate_Business.as_view()),
    # Update business
    path('business/update', UpdateBusiness.as_view()),
    # Fetch Single business
    path('business/fetch-single', FetchSingleBusiness.as_view()),
    # Explore Business
    path('business/explore', ExploreBusiness.as_view()),
    # Business Banners
    path('business/banner', BusinessBanner.as_view()),
    # Fetch Business
    path('business/<str:pk>', ScanBusinessQR.as_view()),
]
