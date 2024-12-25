import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.utils import timezone
from mongoengine import DoesNotExist

from .models import *


class ChatroomConsumer(WebsocketConsumer):

    def connect(self):

        self.user_id = str(self.scope['user'].id)
        # Assuming `user` is authenticated
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        query_params = self.scope['query_string'].decode('utf-8')
        params = dict(param.split('=') for param in query_params.split('&'))
        self.second_user_id = params.get('user_id')

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
            self.chatroom = Chat(
                participants=[self.user_id, self.second_user_id],
                is_active=True,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            self.chatroom.save()

        # Add the WebSocket to the group
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
                raise ValueError("Empty message content.")

            # Save and broadcast the message
            message = Message(
                chat=self.chatroom,
                sender_id=self.user_id,
                content=message_content,
                read=False,
                created_at=timezone.now(),
            )
            message.save()

            async_to_sync(self.channel_layer.group_send)(
                self.chat_id,
                {
                    'type': 'chat_message',
                    'message': {
                        'sender_id': self.user_id,
                        'content': message_content,
                        'created_at': message.created_at.isoformat(),
                    },
                },
            )
        except (json.JSONDecodeError, ValueError) as e:
            self.send(text_data=json.dumps({"error": str(e)}))
        except Exception as e:
            self.send(
                text_data=json.dumps({"error": "An unexpected error occurred."})
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
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id,
            self.channel_name,
        )

        # Optionally mark all unread messages from this chat as read
        Message.objects(
            chat=self.chatroom, read=False, sender_id=self.second_user_id
        ).update(set__read=True)
