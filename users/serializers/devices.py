'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------
Description:
Serializer file for users device token endpoints.
---------------------------------------------------
'''

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models.devices import UserDeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceToken
        fields = ['platform', 'token']

    def validate(self, data):
        token = data.get('token')
        platform = data.get('platform')  # 'android' or 'ios'

        if not token or not platform:
            raise ValidationError({"error": "Token and platform are required."})
        return data

    def save(self):
        # Get the current authenticated user
        user = self.context['request'].user
        platform = self.validated_data['platform']
        token = self.validated_data['token']
        # Check if token already exists for this user and platform
        # todo
        #  we may need to remove existed if token already existed for another user
        device_token, created = UserDeviceToken.objects.update_or_create(
            user=user,
            platform=platform,
            defaults={'token': token},  # Update token if it exists
        )
        return device_token, created
