import phonenumbers
from ..models.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError


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
                raise ValidationError('This is not valid phone number.')

        except phonenumbers.NumberParseException:
            raise ValidationError('This is not valid phone number.')

        return phone

    def validate(self, data):
        phone_number = data.get('phone_number')
        if not phone_number:
            raise ValidationError({'phone_number': 'phone number is required.'})
        self.validate_phone_number(phone_number)
        # Check if the email is valid
        user = User.objects.filter(phone_number=phone_number).first()
        if user:
            raise ValidationError(
                {'Phone number': 'This Phone number is already taken.'}
            )
        return data