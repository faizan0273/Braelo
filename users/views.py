from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .helpers.google import google_auth


from .helpers.helper import response, get_error_details
from .models import User
from .serializers import (
    EmailSignup,
    EmailLogin,
    PhoneSignup,
    GoogleSignup,
)
from django.db import DatabaseError as SQLITE_ERROR


class SignUpWithEmailView(generics.CreateAPIView):
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
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                # Combine user data with token data
                response_data = {'email': user.email, 'token': token_data}
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
            # add username to the validated data
            user.validated_data['username'] = user.validated_data[
                'phone_number'
            ]
            user = user.create(user.validated_data)
            if user:
                # Generate JWT token after user creation
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                # Combine user data with token data
                response_data = {
                    'phone': user.phone_number,
                    'token': token_data,
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


class GoogleCallbackView(generics.CreateAPIView):
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
                refresh = RefreshToken.for_user(_user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                # Combine user data with token data
                response_data = {'email': _user.email, 'token': token_data}
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
            refresh = RefreshToken.for_user(_user)
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            response_data = {'email': _user.email, 'token': token_data}
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


# login part
class LoginWithEmailView(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = []  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.validated_data
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': user.role,  # Include the role in the response if needed
                },
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


# testing


@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')
