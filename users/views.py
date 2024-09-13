import pyotp
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Interest
from .helpers.google_auth import google_auth
from django.db import DatabaseError as SQLITE_ERROR
from .helpers.helper import get_error_details, get_token, response
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
    InterestSerializer,
)


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
                return response(
                    status=status.HTTP_201_CREATED,
                    message='User Signed Up',
                    data=response_data,
                )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data=request.data,
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=request.data,
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=request.data,
                error=str(err),
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
                return response(
                    status=status.HTTP_201_CREATED,
                    message='User Signed Up',
                    data=response_data,
                )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data=request.data,
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=request.data,
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=request.data,
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
                # return Response(response_data, status=status.HTTP_201_CREATED)
                return response(
                    status=status.HTTP_201_CREATED,
                    message='User Signed Up',
                    data=response_data,
                )
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
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=response_data,
                error=error,
            )
            # return Response(response_data, status=status.HTTP_200_OK)
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=request.data,
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=request.data,
                error=str(err),
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
            # Email already exists
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data=request.data,
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=request.data,
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=request.data,
                error=str(err),
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
            return response(
                status=status.HTTP_200_OK,
                message='user Logged in',
                data=response_data,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data=request.data,
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=request.data,
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=request.data,
                error=str(err),
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
    permission_classes = [AllowAny]  # Ensure the user is authenticated
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
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data='',
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data='',
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data='',
                error=str(err),
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
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data='',
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data='',
                error=str(err),
            )

        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data='',
                error=str(err),
            )


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            # Extract the refresh token from request data
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            return response(
                status=status.HTTP_200_OK,
                message='Logged out successfully.',
                data={'refresh_token': refresh_token},
                error='',
            )
        except TokenError as err:
            # Email already exists
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Token Error',
                data='',
                error=str(err),
            )


#
# # List and Create Interest API
# class InterestListCreateView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = InterestSerializer
#     queryset = Interest.objects.all()
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         data['user_id'] = request.user.id
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# # Retrieve, Update, and Delete Interest API
# class InterestDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = InterestSerializer
#     queryset = Interest.objects.all()
#     lookup_field = (
#         'id'  # Use 'id' or '_id' depending on how you're accessing the document
#     )
#


# testing
@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')
