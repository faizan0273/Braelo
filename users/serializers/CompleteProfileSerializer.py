from ..models.models import User
from rest_framework import serializers
from rest_framework.serializers import ValidationError



class CompleteProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, data):
        user = self.context['request'].user

        email = data.get('email')
        phone = data.get('phone')

        if email and phone:
            raise ValidationError(
                'Only one of email or phone should be provided.'
            )

        # If the user already has an email, they can't add one
        if email:
            if user.email:
                raise ValidationError(
                    {'email': 'Email is already set and cannot be changed.'}
                )
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    {'email': 'This email is already in use.'}
                )

        # If the user already has a phone number, they can't add one
        if phone:
            if user.phone_number:
                raise ValidationError(
                    {
                        'phone': 'Phone number is already set and cannot be changed.'
                    }
                )
            if User.objects.filter(phone_number=phone).exists():
                raise ValidationError(
                    {'phone': 'This phone number is already in use.'}
                )

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        validated_data = self.validated_data
        if not validated_data:
            return {}
        # Update the missing information
        if validated_data.get('email'):
            user.email = validated_data['email']
        if validated_data.get('phone'):
            user.phone_number = validated_data['phone']

        user.save()
        return validated_data