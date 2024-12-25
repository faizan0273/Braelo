from django.utils import timezone
from mongoengine import (
    Document,
    StringField,
    ReferenceField,
    DateTimeField,
    BooleanField,
)

from chats.models.chat import Chat


class Message(Document):
    '''
    Message model to represent a single chat message.
    '''

    chat = ReferenceField(Chat, required=True)  # Reference to the Chat document
    sender_id = StringField(required=True)  # Sender's user ID from MySQL
    content = StringField(required=True)  # Message content
    read = BooleanField(default=False)  # Read status for the recipient
    created_at = DateTimeField()

    meta = {
        'collection': 'messages',
        'ordering': ['-created_at'],
        'indexes': [
            'chat',
            (
                'chat',
                'created_at',
            ),
        ],
    }
