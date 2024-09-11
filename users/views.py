from datetime import datetime

import pyotp
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError

from .helpers.google_auth import google_auth


from .helpers.helper import get_error_details, get_token
from .models import User
from .serializers import (
    EmailSignup,
    EmailLogin,
    PhoneSignup,
    GoogleSignup,
    PhoneLogin,
    AppleSignup,
    ForgotPasswordSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)
from django.db import DatabaseError as SQLITE_ERROR


class SignUpWithEmail(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = EmailSignup
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            # add username to the validated data
            user.validated_data['username'] = user.validated_data['email']
            user = user.create(user.validated_data)
            # user = user.save()  # Save the user instance
            if user:
                # Generate JWT token after user creation
                token = get_token(user)
                # Combine user data with token data
                response_data = {'email': user.email, 'token': token}
                return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SignUpWithPhone(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PhoneSignup
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # todo ph#
        #  1. In case of phone number otp generations
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            # Generate the OTP
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret, digits=6)
            otp = totp.now()
            user.validated_data['otp'] = otp
            user.validated_data['otp_created_at'] = datetime.now()
            # todo Send OTP to user's phone
            # send_otp_to_phone(user.phone_number, otp)
            # add username to the validated data
            user.validated_data['username'] = user.validated_data[
                'phone_number'
            ]
            user = user.create(user.validated_data)
            if user:
                # Generate JWT token after user creation
                token = get_token(user)
                # Combine user data with token data
                response_data = {
                    'phone': user.phone_number,
                    'token': token,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Phone already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GoogleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = GoogleSignup

    @csrf_exempt
    def post(self, request):
        token = request.data.get('credential')
        # Google User Details
        g_user = google_auth(token)
        _user = self.get_serializer(data=g_user)
        try:
            _user.is_valid(raise_exception=True)
            # add username to the validated data
            _user.validated_data['username'] = _user.validated_data['email']
            _user = _user.create(_user.validated_data)

            # No user is available for this email create new user to our db
            if _user:
                # Generate JWT token after user creation
                token = get_token(_user)
                # Combine user data with token data
                response_data = {'email': _user.email, 'token': token}
                return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as err:
            error = get_error_details(err.detail)
            if not g_user:
                return Response(
                    {'detail': 'Validation Failed', 'errors': error},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Email already exists
            _user = _user.update(g_user)
            token = get_token(_user)
            response_data = {'email': _user.email, 'token': token}
            return Response(response_data, status=status.HTTP_200_OK)
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AppleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = AppleSignup

    @csrf_exempt
    def post(self, request):
        pass


# login part
class LoginWithPhone(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = PhoneLogin

    def post(self, request, *args, **kwargs):
        data = request.data
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.validated_data
            token = get_token(user)
            response_data = {'phone_number': user.phone_number, 'token': token}
            return Response(
                response_data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Incorrect email & password
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# login part-
class LoginWithEmail(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = [AllowAny]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.validated_data
            token = get_token(user)
            response_data = {'email': user.email, 'token': token}
            return Response(
                response_data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Incorrect email & password
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TokenRefresh(generics.CreateAPIView):
    pass


class ResetPassword(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password reset successful.'},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user.save()
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePassword(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            # our logic
            # Generate password reset token
            # token = default_token_generator.make_token(user)
            # uid = urlsafe_base64_encode(force_bytes(user.pk))
            #
            # # Construct password reset URL (You should implement the frontend link handling)
            # reset_url = f'http://yourfrontend.com/reset-password/{uid}/{token}/'
            #
            # # Send email (You can replace `send_mail` with your custom email service)
            # send_mail(
            #     subject='Password Reset',
            #     message=f'Click the link to reset your password: {reset_url}',
            #     from_email='noreply@yourdomain.com',
            #     recipient_list=[email],
            # )
            #
            # return Response(
            #     {'message': 'Password reset link has been sent to your email.'},
            #     status=status.HTTP_200_OK,
            # )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        # Blacklist the user's token (if using JWT with a blacklist) or handle session invalidation
        return Response(
            {'message': 'Logged out successfully.'}, status=status.HTTP_200_OK
        )


# testing
@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')
