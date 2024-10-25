from datetime import timedelta
from ..models.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError


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
        if not user:
            raise ValidationError(
                {'Phone number': 'No user found with this Phone Number.'}
            )
        if not self.is_otp_valid(phone_number, otp):
            raise ValidationError({'otp': 'The OTP is invalid or has expired.'})
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