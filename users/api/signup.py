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

import random
import phonenumbers
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt


from users.models import User
from users.models import Business

from users.serializers import EmailSignup
from helpers import (
    handle_exceptions,
    get_token,
    response,
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
            'name': user.name,
            'token': token,
            'user_status': user.is_business,
        }
        return response(
            status=status.HTTP_201_CREATED,
            message='User Signed Up',
            data=data,
        )


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

    def generate_username(self):
        '''
        Generates random name used in phone auth
        '''
        number = random.randint(
            1000, 9999999
        )  # Generate a random number with a wide range
        return f"User{number}"

    def authenticate_user(self, login_type, data):
        '''
        Handles sign_up/login for google and apple
        :param request: login_type(apple/google), user_data
        :return: user's signed up status. (json)
        '''
        required_fields = [
            'email',
            f'{login_type}_id',
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
        provider_id = data.get(f'{login_type}_id')
        validate_email(email)

        user_data = {
            'email': email,
            f'{login_type}_id': provider_id,
            'username': data.get('name'),
            'name': data.get('name'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'is_email_verified': data.get('is_email_verified'),
        }

        user = User.objects.filter(email=email).first()

        if user:
            existing_provider_id = getattr(user, f'{login_type}_id', None)
            if (
                existing_provider_id is not None
                and existing_provider_id != provider_id
            ):
                raise ValidationError({f'{login_type}_id': 'incorrect'})

            if existing_provider_id is None:
                setattr(user, f'{login_type}_id', provider_id)
                user.save()

            token = get_token(user)
            business = Business.objects.filter(user_id=user.id).first()
            response_data = {
                'email': user.email,
                'name': user.name,
                'business_name': business.business_name if business else None,
                'token': token,
                'user_status': user.is_business,
            }
            return response_data

        provider_id_check = User.objects.filter(
            **{f'{login_type}_id': provider_id}
        ).exists()
        if provider_id_check:
            raise ValidationError(
                {f'{login_type}_id': 'Already exists for another user'}
            )

        new_user = User.objects.create(**user_data)
        new_token = get_token(new_user)
        response_data = {
            'email': new_user.email,
            'name': new_user.name,
            'token': new_token,
            'user_status': new_user.is_business,
        }
        return response_data

    @handle_exceptions
    @csrf_exempt
    def post(self, request):
        '''
        POST method to handle user signup/login on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''

        login_type = request.GET.get('login_type')
        if login_type not in ('google', 'apple', 'phone'):
            raise ValidationError(
                {'Type': 'Must be ["google","apple","phone"]'}
            )
        if login_type in ['google', 'apple']:
            data = self.authenticate_user(login_type, request.data)
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=data,
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
                business = Business.objects.filter(user_id=user.id).first()
                data = {
                    'phone': user.phone_number,
                    'business_name': (
                        business.business_name if business else None
                    ),
                    'token': token,
                    'user_status': user.is_business,
                }
                return response(
                    status=status.HTTP_200_OK,
                    message='User logged in',
                    data=data,
                )
            username = self.generate_username()
            new_user = User.objects.create(
                username=username,
                name=username,
                first_name=username,
                last_name=username,
                phone_number=phone_number,
            )
            token = get_token(new_user)
            data = {
                'phone': new_user.phone_number,
                'name': new_user.name,
                'token': token,
                'user_status': new_user.is_business,
            }
            return response(
                status=status.HTTP_200_OK,
                message='User logged in',
                data=data,
            )
