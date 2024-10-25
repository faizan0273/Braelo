'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User sign up end-points module.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt


from ..models import User

from ..serializers import (
    EmailSignup,
    PhoneSignup,
    GoogleSignup,
    AppleSignup,
)
from ..helpers import (
    handle_exceptions,
    get_token,
    response,
    google_auth,
    get_error_details,
)


class SignUpWithEmail(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = EmailSignup
    permission_classes = [AllowAny]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user sign up on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        # add username to the validated data
        user.validated_data['username'] = user.validated_data['email']
        user = user.create(user.validated_data)
        if not user:
            # todo: needs better logic
            raise Exception('Cannot Add user to Database')
        # Generate JWT token after user creation
        token = get_token(user)
        # Combine user data with token data
        data = {'email': user.email, 'token': token}
        return response(
            status=status.HTTP_201_CREATED,
            message='User Signed Up',
            data=data,
        )


class SignUpWithPhone(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PhoneSignup
    permission_classes = [AllowAny]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user sign up on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        # todo ph#
        #  1. In case of phone number otp generations
        resp = request.data
        user = self.get_serializer(data=resp)
        user.is_valid(raise_exception=True)
        user.validated_data['username'] = user.validated_data['phone_number']
        user = user.create(user.validated_data)
        if not user:
            raise Exception('Cannot Add user to Database')
        # Generate JWT token after user creation
        token = get_token(user)
        # Combine user data with token data
        data = {
            'phone': user.phone_number,
            'token': token,
        }
        return response(
            status=status.HTTP_201_CREATED,
            message='User Signed Up',
            data=data,
        )


class GoogleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = GoogleSignup

    @handle_exceptions
    @csrf_exempt
    def post(self, request):
        '''
        POST method to handle user signup/login on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        token = request.data.get('credential')
        # Google User Details
        g_user = google_auth(token)
        _user = self.get_serializer(data=g_user)
        try:
            _user.is_valid(raise_exception=True)
            # add username to the validated data
            _user.validated_data['username'] = _user.validated_data['email']
            _user = _user.create(_user.validated_data)
            if not _user:
                raise Exception('Cannot Add user to Database')
            # No user is available for this email create new user to our db
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
                return response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='Validation Error',
                    data={},
                    error=error,
                )

            # Email already exists
            _user = _user.update(g_user)
            token = get_token(_user)
            response_data = {'email': _user.email, 'token': token}
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=response_data,
            )


class AppleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = AppleSignup

    @csrf_exempt
    def post(self, request):
        pass
