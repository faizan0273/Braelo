'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
consumer socket file.
---------------------------------------------------
'''

import json

from asgiref.sync import async_to_sync
from channels.exceptions import DenyConnection
from channels.generic.websocket import WebsocketConsumer

from django.utils import timezone
from mongoengine import DoesNotExist

from .models import *

connected_users = {}


class ChatroomConsumer(WebsocketConsumer):
    '''
    WebSocket handler.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_type = None
        self.chatroom = None
        self.second_user_id = None
        self.chat_id = None
        self.user_id = None

    def connect(self):
        '''
        WebSocket connect handler.
        '''
        if not self.scope['user'].is_authenticated:
            raise DenyConnection('Invalid or expired token.')
        self.user_id = str(self.scope['user'].id)
        # Assuming `user` is authenticated
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        query_params = self.scope['query_string'].decode('utf-8')
        params = dict(param.split('=') for param in query_params.split('&'))
        self.second_user_id = params.get('user_id')
        self.chat_type = 'private'
        # second user id is important
        if not self.second_user_id:
            self.close()
            return

        # Ensure chat exists or create it (one-on-one chat setup)
        try:
            self.chatroom = Chat.objects.get(
                chat_id=self.chat_id,
                participants__all=[self.user_id, self.second_user_id],
                participants__size=2,
            )
        except DoesNotExist:
            raise DenyConnection('Chat matching query does not exist.')

        # Determine if it's a private or group chat
        if len(self.chatroom.participants) == 2:
            self.chat_type = 'group'
        connected_users[self.user_id] = self.channel_name
        # Add the WebSocket to the group
        if self.chat_type == 'group':
            async_to_sync(self.channel_layer.group_add)(
                self.user_id, self.channel_name
            )
        self.accept()

    def receive(self, text_data):
        '''
        Handles incoming WebSocket messages from the client.
        '''
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get('message')
            if not message_content:
                self.send(
                    text_data=json.dumps({'error': 'Empty message content.'})
                )
                return

            # Save and broadcast the message
            message = Message(
                chat=self.chatroom,
                sender_id=self.user_id,
                content=message_content,
                read=False,
                created_at=timezone.now(),
            )
            message.save()

            message_payload = {
                'sender_id': self.user_id,
                'content': message_content,
                'created_at': message.created_at.isoformat(),
            }

            # For group chat, send to all participants in the group
            if self.chat_type == 'group':
                async_to_sync(self.channel_layer.group_send)(
                    self.chat_id,
                    {
                        'type': 'chat_message',
                        'message': message_payload,
                    },
                )

            # For private chat, send directly to the other user (if connected)
            recipient_id = None
            for user in self.chatroom.participants:
                if user != self.user_id:
                    recipient_id = user
                    break
            if not recipient_id:
                self.send(
                    text_data=json.dumps({'error': 'No recipient found.'})
                )
            # The other participant

            # Send message to recipient if they are connected
            if recipient_id in connected_users:
                async_to_sync(self.channel_layer.send)(
                    connected_users[recipient_id],
                    {
                        'type': 'chat_message',
                        'message': message_payload,
                    },
                )

        except (json.JSONDecodeError, ValueError) as e:
            self.send(text_data=json.dumps({'error': str(e)}))
        except Exception as e:
            self.send(
                text_data=json.dumps({'error': 'An unexpected error occurred.'})
            )

    def chat_message(self, event):
        '''
        Event handler for broadcasting messages to WebSocket clients in the group.
        '''
        self.send(text_data=json.dumps(event['message']))

    def disconnect(self, close_code):
        '''
        Handles WebSocket disconnections.
        '''
        # Remove the user from the connected users
        if self.user_id in connected_users:
            del connected_users[self.user_id]

        if not getattr(self, 'chat_id', None):
            return
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id,
            self.channel_name,
        )

        # Optionally mark all unread messages from this chat as read
        Message.objects(
            chat=self.chatroom, read=False, sender_id=self.second_user_id
        ).update(set__read=True)
