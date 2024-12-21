'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notifications operations endpoints.
---------------------------------------------------
'''

from rest_framework import serializers
from notifications.models import Notification


class MarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    def save(self):
        # Mark notifications as read
        ...


class DeleteNotificationSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    def save(self):
        # Delete notifications
        ...
