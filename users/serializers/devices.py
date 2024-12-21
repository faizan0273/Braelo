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

from rest_framework_mongoengine import serializers

from rest_framework.exceptions import ValidationError

from users.models.devices import UserDeviceToken


class DeviceTokenSerializer(serializers.DocumentSerializer):

    class Meta:
        model = UserDeviceToken
        fields = '__all__'

    def validate(self, data):
        token = data.get('token')
        platform = data.get('platform')  # 'android' or 'ios'

        if not token or not platform:
            raise ValidationError({'error': 'Token and platform are required.'})
        return data

    def save(self):
        # Get the current authenticated user
        user = self.context['request'].user
        platform = self.validated_data['platform']
        token = self.validated_data['token']
        # Check if token already exists for this user and platform
        # todo
        #  we may need to remove existed if token already existed for another user
        existing_token = UserDeviceToken.objects(token=token).first()
        if existing_token and existing_token.user_id != user.id:
            existing_token.delete()

        # Update or create the device token
        device_token = UserDeviceToken.objects(
            user_id=user.id, platform=platform
        ).modify(
            upsert=True,
            new=True,
            set__token=token,
            set__email=user.email,
        )
        return device_token
