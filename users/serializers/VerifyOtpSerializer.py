from ..models.models import OTP
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self, data):
        otp = data.get('otp')
        email = data.get('email')
        try:
            otp_record = OTP.objects.get(user__email=email, otp=otp)
        except OTP.DoesNotExist:
            raise ValidationError('Invalid OTP or email.')
        if otp_record.has_expired():
            raise ValidationError('This OTP has expired.')
        data['otp_record'] = otp_record
        return data