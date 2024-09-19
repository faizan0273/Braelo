'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for users based endpoints
---------------------------------------------------
'''

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from mongoengine import DoesNotExist

from .models.interests import Interest
from .models.models import User

import phonenumbers
from rest_framework import serializers
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


############################################################################
#                                                                          #
#                                  Sign up                                 #
#                                                                          #
############################################################################

# todo Add role in all


class EmailSignup(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            # Check if the email is valid
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError(
                {'email': 'Enter a valid email address.'}
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'This email is already taken.'}
            )
        # Password validation
        if not password:
            raise serializers.ValidationError(
                {'password': 'Password is required.'}
            )
        # data['password'] = make_password(password)
        return data

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            validated_data['is_email_verified'] = True
            user = User.objects.create_user(**validated_data)
            return user
            # user = User(**validated_data)
            # if user.save():
            #     return user
        return None

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance


class PhoneSignup(serializers.Serializer):
    phone_number = serializers.CharField(
        min_length=11, max_length=15, required=True
    )

    class Meta:
        model = User
        fields = ['phone_number']

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            validated_data['is_phone_verified'] = True
            user = User.objects.create_user(**validated_data)
            return user
        return False

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
                raise serializers.ValidationError(
                    'This is not valid phone number.'
                )

        except phonenumbers.NumberParseException:
            raise serializers.ValidationError('This is not valid phone number.')

        return phone

    def validate(self, data):
        phone_number = data.get('phone_number')
        if phone_number:
            self.validate_phone_number(phone_number)
            # Check if the email is valid
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                raise serializers.ValidationError(
                    {'Phone number': 'This Phone number is already taken.'}
                )
        return data


class GoogleSignup(serializers.Serializer):
    '''
    CRUD operation for User.
    '''

    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    google_id = serializers.CharField(
        min_length=11, max_length=255, required=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    is_email_verified = serializers.BooleanField(default=False)
    is_phone_verified = serializers.BooleanField(default=False)

    def validate(self, data):
        '''
        Check that the email or phone number is not already taken.
        '''
        email = data.get('email')
        google_id = data.get('google_id')
        if email and User.objects.filter(email=email).first():
            raise serializers.ValidationError(
                {'email': 'This email is already taken.'}
            )

        if google_id and User.objects.filter(google_id=google_id).first():
            raise serializers.ValidationError(
                {'google_id': 'This Google ID is already taken.'}
            )
        return data

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            user = User.objects.create_user(**validated_data)
            return user
            # return True
        return False

    def update(self, google_user, **kwargs):
        '''
        Update the user details if any of the provided updated_user_data
        differ from the existing data in the user object.
        :param google_user: Dictionary containing updated user data from Google.(dict)
        :return:
        '''
        user = User.objects.filter(email=google_user['email']).first()
        is_updated = (
            user.name != google_user['name']
            or user.first_name != google_user['first_name']
            or user.last_name != google_user['last_name']
            or user.is_email_verified != google_user['is_email_verified']
            or user.google_id != google_user['google_id']
        )
        if is_updated:
            user.name = google_user['name']
            user.first_name = google_user['first_name']
            user.last_name = google_user['last_name']
            user.is_email_verified = google_user['is_email_verified']
            user.google_id = google_user['google_id']
            user.updated_at = timezone.now()
            user.save()
        return user


class AppleSignup(serializers.Serializer):
    '''
    CRUD operation for User.
    '''

    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    google_id = serializers.CharField(
        min_length=11, max_length=255, required=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    is_email_verified = serializers.BooleanField(default=False)
    is_phone_verified = serializers.BooleanField(default=False)

    def validate(self, data):
        '''
        Check that the email or phone number is not already taken.
        '''
        # directories
        email = data['']
        email = data.get('email')
        google_id = data.get('google_id')
        if email and User.objects.filter(email=email).first():
            raise serializers.ValidationError(
                {'email': 'This email is already taken.'}
            )

        if google_id and User.objects.filter(google_id=google_id).first():
            raise serializers.ValidationError(
                {'google_id': 'This Google ID is already taken.'}
            )
        return data

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            user = User.objects.create_user(**validated_data)
            return user
            # return True
        return False

    def update(self, google_user, **kwargs):
        '''
        Update the user details if any of the provided updated_user_data
        differ from the existing data in the user object.
        :param google_user: Dictionary containing updated user data from Google.(dict)
        :return:
        '''
        user = User.objects.filter(email=google_user['email']).first()
        is_updated = (
            user.name != google_user['name']
            or user.first_name != google_user['first_name']
            or user.last_name != google_user['last_name']
            or user.is_email_verified != google_user['is_email_verified']
            or user.google_id != google_user['google_id']
        )
        if is_updated:
            user.name = google_user['name']
            user.first_name = google_user['first_name']
            user.last_name = google_user['last_name']
            user.is_email_verified = google_user['is_email_verified']
            user.google_id = google_user['google_id']
            user.updated_at = timezone.now()
            user.save()
        return user


############################################################################
#                                                                          #
#                                   Login                                  #
#                                                                          #
############################################################################


class PhoneLogin(serializers.Serializer):
    phone_number = serializers.CharField(
        min_length=11, max_length=15, required=True
    )
    otp = serializers.CharField(min_length=6, max_length=6, required=True)

    class Meta:
        model = User
        fields = ['phone_number']

    def validate(self, data):
        otp = data.get('otp')
        phone_number = data.get('phone_number')
        # Check if the user with the provided email exists
        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise serializers.ValidationError(
                {'Phone number': 'No user found with this Phone Number.'}
            )
        if not self.is_otp_valid(phone_number, otp):
            raise serializers.ValidationError(
                {'otp': 'The OTP is invalid or has expired.'}
            )
        return user

    def is_otp_valid(self, phone, otp):
        '''
        Validates otp and phone number.
        :param phone: phone number. (string)
        :param otp: otp code. (int)
        :return: True if validates, otherwise false.(boolean)
        '''
        user = User.objects.filter(phone_number=phone, otp=otp).first()
        if not user:
            return False
        # Temporary adding day 1 limit for testing
        expiry_time = user.otp_created_at + timedelta(days=1)
        return timezone.now() < expiry_time


class EmailLogin(serializers.Serializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        # Check if the user with the provided email exists
        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                {'email': 'No user found with this email address.'}
            )

        # Check if the provided password matches the stored password
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                {'password': 'Incorrect password.'}
            )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        '''
        Check that the old password still exists.
        '''
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = User.objects.filter(email=data['email']).first()
        if user is None:
            raise serializers.ValidationError(
                {'email': 'No user found with this email address.'}
            )
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {'old_password': ['Incorrect password.']}
            )
        if old_password == new_password:
            raise serializers.ValidationError(
                {
                    'new_password': 'New password cannot be the same as the old password.'
                }
            )
        # todo: Apply this check
        #  validate_password(new_password, user=user)

        return data

    def save(self, **kwargs):
        email = self.validated_data.get('email')
        new_password = self.validated_data.get('new_password')
        with transaction.atomic():
            # Fetch the user and set the new password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            return {'email': user.email}


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        '''
        Validate that the email exists in the database.
        '''
        email = data.get('email')
        user = User.objects.filter(email=email).exists()
        if not user:
            raise serializers.ValidationError(
                'No user found with this email address.'
            )
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField()  # Reset token

    # def validate(self, data):
    #     '''
    #     Validate the token and UID, and check if they match.
    #     '''
    #     user = User.objects.get(email=data.get('email'))
    #     if not user:
    #         raise serializers.ValidationError(
    #             'Invalid email or user does not exist.'
    #         )
    #
    #     # Check the token validity
    #     if not default_token_generator.check_token(user, data.get('token')):
    #         raise serializers.ValidationError('Invalid or expired token.')
    #
    #     return data

    def save(self):
        '''
        Set the new password for the user.
        '''
        uid = urlsafe_base64_decode(self.validated_data.get('uidb64')).decode()
        user = User.objects.get(pk=uid)
        new_password = self.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return user


class InterestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    def validate_tags(self, tags):
        '''
        Check if the provided tags are correct.
        :param tags: tags from request. (list)
        :return: return tags If it exists | exception. (list)
        '''
        for tag in tags:
            if tag not in INTERESTS:
                raise serializers.ValidationError({'tags': 'Incorrect tag.'})
        return tags

    def validate_user_id(self, user_id):
        '''
        Check if the user_id already exists.
        :param user_id: id of user from mysql db. (int)
        :return: If it exists, return the existing object for update | user_id.
        '''
        try:
            # If user_id exists, return the corresponding Interest object (for updating)
            interest = Interest.objects.get(user_id=user_id)
            return interest
        except DoesNotExist:
            # If user_id does not exist, return the user_id (for creating a new entry)
            return user_id

    def create(self, validated_data):
        '''
        Create a new interest record for a user if it doesn't already exist.
        '''
        return Interest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''
        Update the existing interest record for a user.
        '''
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance

    def save(self, **kwargs):
        '''
        Save or update the user interest based on whether the user_id exists.
        '''
        interest = self.validated_data.get('user_id')

        if isinstance(interest, Interest):
            # If the validate_user_id returned an existing object, update it
            return self.update(interest, self.validated_data)
        else:
            # Otherwise, create a new interest
            return self.create(self.validated_data)
