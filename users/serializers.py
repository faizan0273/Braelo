# users/serializers.py
from datetime import datetime

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
            validated_data['created_at'] = datetime.now()
            validated_data['updated_at'] = datetime.now()
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


############################################################################
#                                                                          #
#                                   Login                                  #
#                                                                          #
############################################################################


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
