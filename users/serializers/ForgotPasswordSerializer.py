from ..models.models import User
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        '''
        Validate that the email exists in the database.
        '''
        email = data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError('No user found with this email address.')
        data['user'] = user
        return data