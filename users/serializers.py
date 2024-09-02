# users/serializers.py
from datetime import timedelta
from django.utils import timezone


import phonenumbers

from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'phone_number',
            'name',
            'last_name',
            'role',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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
                {"email": "Enter a valid email address."}
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "This email is already taken."}
            )
        # Password validation
        if not password:
            raise serializers.ValidationError(
                {"password": "Password is required."}
            )
        # data['password'] = make_password(password)
        return data

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            validated_data['is_email_verified'] = True
            validated_data['password'] = make_password(
                validated_data['password']
            )
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
        """
        Check if the phone number is valid.
        """
        try:
            # Parsing phone number
            parsed_number = phonenumbers.parse(phone, None)

            # Checking if the parsed number is a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    "This is not valid phone number."
                )

        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("This is not valid phone number.")

        return phone

    def validate(self, data):
        phone_number = data.get('phone_number')
        if phone_number:
            self.validate_phone_number(phone_number)
            # Check if the email is valid
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                raise serializers.ValidationError(
                    {"Phone number": "This Phone number is already taken."}
                )
        return data


class GoogleSignup(serializers.Serializer):
    """
    CRUD operation for User.
    """

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
        """
        Check that the email or phone number is not already taken.
        """
        email = data.get('email')
        google_id = data.get('google_id')
        if email and User.objects.filter(email=email).first():
            raise serializers.ValidationError(
                {"email": "This email is already taken."}
            )

        if google_id and User.objects.filter(google_id=google_id).first():
            raise serializers.ValidationError(
                {"google_id": "This Google ID is already taken."}
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

    def update(self, google_user):
        """
        Update the user details if any of the provided updated_user_data
        differ from the existing data in the user object.
        :param google_user: Dictionary containing updated user data from Google.(dict)
        :return:
        """
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
                {"Phone number": "No user found with this Phone Number."}
            )
        if not self.is_otp_valid(phone_number, otp):
            raise serializers.ValidationError(
                {"otp": "The OTP is invalid or has expired."}
            )
        return user

    def is_otp_valid(self, phone, otp):
        """
        Validates otp and phone number
        :param phone: phone number. (string)
        :param otp: otp code. (int)
        :return: True if validates, otherwise false.(boolean)
        """
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
                {"email": "No user found with this email address."}
            )

        # Check if the provided password matches the stored password
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                {"password": "Incorrect password."}
            )
        return user
