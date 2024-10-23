from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken



class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate_refresh(self, value):
        '''
        Check if the refresh token has already been blacklisted.
        '''
        try:
            # Try to retrieve the refresh token
            token = RefreshToken(value)

            # Check if the token is already blacklisted
            if BlacklistedToken.objects.filter(
                token__jti=token['jti']
            ).exists():
                raise ValidationError(
                    'This token has already been blacklisted.'
                )
        except Exception as exc:
            raise ValidationError(str(exc))

        return value
