'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notifications endpoints.
---------------------------------------------------
'''

from rest_framework import serializers

from helpers.notifications import send_fcm_notification
from notifications.models import Notification


class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'body', 'type', 'target_users']

    def validate(self, data):
        '''
        Validate notification details before saving.
        '''
        if not data.get('title'):
            raise serializers.ValidationError({'title': 'Title is required.'})
        if not data.get('body'):
            raise serializers.ValidationError({'body': 'Body is required.'})
        if not data.get('type'):
            raise serializers.ValidationError({'type': 'Type is required.'})

        # todo Optionally add more validations, e.g., valid type or user checks.
        return data

    def save(self):
        '''
        Save notification details in MongoDB and send it to FCM.
        '''
        title = self.validated_data['title']
        body = self.validated_data['body']
        type = self.validated_data['type']
        target_users = self.validated_data['target_users']

        # Save to MongoDB
        notification_doc = Notification(
            title=title,
            body=body,
            type=type,
            target_users=target_users,
        )
        notification_doc.save()

        # Send notification via FCM
        if target_users:
            # Send to specific users
            for user in target_users:
                send_fcm_notification(user, title, body)
        else:
            # Broadcast notification
            from django.contrib.auth import get_user_model

            User = get_user_model()
            all_users = User.objects.all()
            for user in all_users:
                send_fcm_notification(user.id, title, body)

        return notification_doc
