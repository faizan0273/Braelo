from ..models.models import User
from django.utils import timezone
from rest_framework import serializers
from django.core.validators import validate_email
from rest_framework.serializers import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError



def _validate_email(email):
    '''
    Validates given email.
    :param email: email address. (string)
    :return: email address. (string)
    '''
    try:
        validate_email(email)
        return email
    except DjangoValidationError:
        raise ValidationError({'email': 'Enter a valid email address.'})


############################################################################
#                                                                          #
#                                  Sign up                                 #
#                                                                          #
############################################################################


class EmailSignup(serializers.Serializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email:
            raise ValidationError({'email': 'Email is required.'})
        if not password:
            raise ValidationError({'password': 'Password is required.'})
        email = _validate_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already taken.'})
        # Password validation
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
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance
