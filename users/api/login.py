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

from ..models import User
from ..helpers import handle_exceptions
from ..serializers import EmailLogin, PhoneLogin
from ..helpers.helper import get_token, response


# login part
class LoginWithPhone(generics.CreateAPIView):
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
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
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
    pass


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        # Blacklist the user's token (if using JWT with a blacklist) or handle session invalidation
        return Response(
            {'message': 'Logged out successfully.'}, status=status.HTTP_200_OK
        )
