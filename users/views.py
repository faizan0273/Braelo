from django.shortcuts import render

# Create your views here.
# users/views.py

from rest_framework import generics, permissions, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .helpers.helper import response, get_error_details
from .models import User
from .serializers import UserSerializer, EmailSignup, EmailLogin
from django.db import DatabaseError as SQLITE_ERROR


def google_user_payload(record):
    """
    Creates our schema payload of Google user.
    :param record: google api information. (dict)
    :return: parsed payload. (dict)
    """
    user = {
        'name': record['name'],
        'email': record['email'],
        'google_id': record['sub'],
        'first_name': record['given_name'],
        'last_name': record['family_name'],
        'is_email_verified': record['email_verified'],
    }
    return user


class SignUpWithEmailView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = EmailSignup
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
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


# login part
class LoginWithEmailView(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = []  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        data = request.data
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
