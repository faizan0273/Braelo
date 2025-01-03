'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notifications for events (like, saved) endpoints.
---------------------------------------------------
'''

from firebase_admin import messaging
from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError

from notifications.models import Notification
from users.models import UserDeviceToken


class EventNotificationSerializer(serializers.DocumentSerializer):

    class Meta:
        model = Notification
        # fields = ['type', 'title', 'body']

    def validate(self, data):
        '''
        Validates the required fields.
        Ensures that the `type`, `title`, `body` are provided, and `data` is a valid dictionary.
        '''
        notify_type = data.get('type')
        title = data.get('title')
        body = data.get('body')
        user_id = data.get('user_id')
        # data = data.get('data', {})

        if not notify_type:
            raise ValidationError({'type': 'Valid type is required.'})
        if not title:
            raise ValidationError({'title': 'Title is required.'})
        if not body:
            raise ValidationError({'body': 'Body is required.'})
        if not user_id:
            raise ValidationError({'user_id': 'Recipient user_id is required.'})

        return data

    def create(self, validated_data):
        '''
        Save notification for event-triggered notifications like chat, listing interactions.
        '''
        title = validated_data['title']
        body = validated_data['body']
        user_id = validated_data['user_id']

        # Create the notification object and save it
        notification = Notification.objects.create(**validated_data)

        # Get device tokens
        device_tokens = self.get_device_token(user_id)
        if not device_tokens:
            raise ValidationError(
                {'user_id': 'No device token found for user_id.'}
            )

        # Add notification_id to the data dictionary after the notification is saved
        notification.data['notification_id'] = str(notification.id)
        notification.save()

        # Send the Firebase notifications
        self.send_fcm_notification(
            device_tokens, title, body, notification.data
        )

        return notification

    def send_fcm_notification(self, device_tokens, title, body, data):
        '''
        Sends the notification via Firebase Cloud Messaging (FCM).
        For now, using hardcoded device tokens.
        '''
        if not device_tokens:
            print('No device tokens provided for FCM notification.')
            return

        data = {key: str(value) for key, value in data.items()}

        # Prepare the FCM message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            tokens=device_tokens,
        )

        # Send notification using Firebase SDK

        messaging.send_each_for_multicast(message)

    def get_device_token(self, user_ids):
        '''
        Fetch the device token for the specified user.
        Replace this with your actual logic to fetch the token.
        '''
        try:
            # Assuming a Device model that stores user_id and device tokens
            devices = UserDeviceToken.objects.filter(user_id__in=user_ids)
            device_tokens = []

            # Iterate over devices and store their tokens in the dictionary
            for device in devices:
                device_tokens.append(device.token)

            return device_tokens
            # return device.token if device else None
        except Exception as e:
            print(f'Error fetching device token for user_id={user_ids}: {e}')
            return None
