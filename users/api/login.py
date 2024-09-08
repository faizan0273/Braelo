'''
@author: Hamid
Date: 14 Aug, 2024
'''

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError

from ..models import User
from ..serializers import EmailLogin, PhoneLogin
from ..helpers.helper import get_error_details, get_token

from django.db import DatabaseError as SQLITE_ERROR


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
    permission_classes = []  # Ensure the user is authenticated

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


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        # Blacklist the user's token (if using JWT with a blacklist) or handle session invalidation
        return Response(
            {'message': 'Logged out successfully.'}, status=status.HTTP_200_OK
        )
