from ..models.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import check_password




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
        if not user:
            raise ValidationError(
                {'email': 'No user found with this email address.'}
            )

        # Check if the provided password matches the stored password
        if not check_password(password, user.password):
            raise ValidationError({'password': 'Incorrect password.'})
        return user


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        '''
        Check that the old password still exists.
        '''
        current_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise ValidationError(
                {'email': 'No user found with this email address.'}
            )
        if not user.check_password(current_password):
            raise ValidationError({'old_password': ['Incorrect password.']})
        if current_password == new_password:
            raise ValidationError(
                {
                    'new_password': 'New password cannot be the same as the old password.'
                }
            )
        if new_password != confirm_password:
            raise ValidationError(
                {
                    'new_password': 'The new password and confirmation password do not match.'
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
