'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User Login end-points module.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..helpers import handle_exceptions
from ..serializers import EmailLogin, PhoneLogin
from ..helpers.helper import get_token, response


# login part
class VerifyOTP(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = PhoneLogin

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user login in on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        user = user.validated_data
        token = get_token(user)
        response_data = {'phone_number': user.phone_number, 'token': token}
        return response(
            status=status.HTTP_200_OK,
            message='user Logged in',
            data=response_data,
        )


class LoginWithEmail(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = [AllowAny]  # Ensure the user is authenticated

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user login on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
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


class TokenRefresh(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        '''
        POST method to handle JWT token refreshing.
        :param request: request object containing refresh token.
        :return: new access token if refresh token is valid.
        '''
        return super().post(request, *args, **kwargs)


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to handle user logout from applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
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
