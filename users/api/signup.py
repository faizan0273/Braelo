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

import phonenumbers
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt


from users.models import User

from users.serializers import (
    EmailSignup,
    PhoneSignup,
    GoogleSignup,
    AppleSignup,
)
from helpers import (
    handle_exceptions,
    get_token,
    response,
    google_auth,
    get_error_details,
)

GOOGLE_OAUTH_CLIENT_ID = (
    "440558817572-e0bjge0jme6oavdeuggfi0a4gukejk87.apps.googleusercontent.com"
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
        data = {
            'email': user.email,
            'token': token,
            'user_status': user.is_business,
        }
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
            'user_status': user.is_business,
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
        # Google User Details
        data = request.data
        required_fields = [
            'email',
            'google_id',
            'name',
            'first_name',
            'last_name',
            'is_email_verified',
        ]
        missing_fields = [
            field for field in required_fields if field not in data
        ]

        if missing_fields:
            raise ValidationError(
                {field: f"{field} is required." for field in missing_fields}
            )

        email = data.get('email')
        google_id = data.get('google_id')
        validate_email(email)
        g_user = {
            'email': email,
            'google_id': google_id,
            'username': email,
            'name': data.get('name'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'is_email_verified': data.get('is_email_verified'),
        }

        user = User.objects.filter(email=email).first()

        if user:
            if user.google_id != google_id:
                raise ValidationError({'google_id': 'incorrect'})
            # incase user ezists will only email
            if not user.google_id:
                user.google_id = google_id
                user.save()
            token = get_token(user)
            response_data = {'email': user.email, 'token': token}
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=response_data,
            )
        google_id_check = User.objects.filter(google_id=google_id).exists()
        if google_id_check:
            raise ValidationError(
                {'google_id': 'Already exists for another user'}
            )
        new_user = User.objects.create(**g_user)
        new_token = get_token(new_user)
        response_data = {'email': new_user.email, 'token': new_token}
        return response(
            status=status.HTTP_200_OK,
            message='user logged in',
            data=response_data,
        )

        # user = self.get_serializer(data=data, context={'request':request})

        # try:
        #     user.is_valid(raise_exception=True)
        #     user.save()
        #     # Generate JWT token after user creation
        #     token = get_token(user)
        #     # Combine user data with token data
        #     response_data = {'email': user.email, 'token': token}
        #     # return Response(response_data, status=status.HTTP_201_CREATED)
        #     return response(
        #         status=status.HTTP_200_OK,
        #         message='User Signed Up',
        #         data=response_data,
        #     )
        # except ValidationError as err:
        #     error = get_error_details(err.detail)
        #     return response(
        #             status=status.HTTP_400_BAD_REQUEST,
        #             message='Validation Error',
        #             data={},
        #             error=error,
        #         )

        # Email already exists
        # _user = _user.update(g_user)
        # token = get_token(_user)
        # response_data = {'email': _user.email, 'token': token}
        # return response(
        #     status=status.HTTP_200_OK,
        #     message='user logged in',
        #     data=response_data,
        # )


class AppleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = AppleSignup

    @csrf_exempt
    def post(self, request):
        pass


class LoginAuth(generics.CreateAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def validate_phone_number(phone):
        '''
        Check if the phone number is valid.
        '''
        try:
            # Parsing phone number
            parsed_number = phonenumbers.parse(phone, None)
            # Checking if the parsed number is a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError('This is not valid phone number.')
        except phonenumbers.NumberParseException:
            raise ValidationError('This is not valid phone number.')
        return phone

    @handle_exceptions
    @csrf_exempt
    def post(self, request):

        login_type = request.GET.get('login_type')
        if login_type not in ('google', 'apple', 'phone'):
            raise ValidationError(
                {'Type': 'Must be ["google","apple","phone"]'}
            )
        # if users logs in from google
        if login_type == 'google':
            data = request.data
            required_fields = [
                'email',
                'google_id',
                'name',
                'first_name',
                'last_name',
                'is_email_verified',
            ]
            missing_fields = [
                field for field in required_fields if field not in data
            ]

            if missing_fields:
                raise ValidationError(
                    {field: f"{field} is required." for field in missing_fields}
                )

            email = data.get('email')
            google_id = data.get('google_id')
            validate_email(email)
            g_user = {
                'email': email,
                'google_id': google_id,
                'username': email,
                'name': data.get('name'),
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'is_email_verified': data.get('is_email_verified'),
            }

            user = User.objects.filter(email=email).first()

            if user:
                if user.google_id != google_id:
                    raise ValidationError({'google_id': 'incorrect'})
                # incase user exists with only email
                if not user.google_id:
                    user.google_id = google_id
                    user.save()
                token = get_token(user)
                response_data = {'email': user.email, 'token': token}
                return response(
                    status=status.HTTP_200_OK,
                    message='user logged in',
                    data=response_data,
                )
            google_id_check = User.objects.filter(google_id=google_id).exists()
            if google_id_check:
                raise ValidationError(
                    {'google_id': 'Already exists for another user'}
                )
            new_user = User.objects.create(**g_user)
            new_token = get_token(new_user)
            response_data = {
                'email': new_user.email,
                'token': new_token,
                'user_status': user.is_business,
            }
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=response_data,
            )
        # if user logs in from phone
        if login_type == 'phone':
            data = request.data
            phone_number = data.get('phone_number')
            if not phone_number:
                raise ValidationError(
                    {'phone_number': 'phone number is required.'}
                )
            self.validate_phone_number(phone_number)
            # Check if the phone_number exists
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                token = get_token(user)
                data = {
                    'phone': user.phone_number,
                    'token': token,
                    'user_status': user.is_business,
                }
                return response(
                    status=status.HTTP_200_OK,
                    message='User logged in',
                    data=data,
                )
            new_user = User.objects.create(
                username=phone_number, phone_number=phone_number
            )
            token = get_token(new_user)
            data = {
                'phone': new_user.phone_number,
                'token': token,
                'user_status': new_user.is_business,
            }
            return response(
                status=status.HTTP_200_OK,
                message='User logged in',
                data=data,
            )
