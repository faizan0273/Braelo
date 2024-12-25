import shortuuid
from mongoengine import (
    Document,
    StringField,
    ListField,
    DateTimeField,
    ReferenceField,
    BooleanField,
)
from django.utils import timezone


class Chat(Document):
    '''
    Chat model to represent a conversation between two users.
    '''

    chat_id = StringField(unique=True)
    participants = ListField(StringField(), required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        'collection': 'chats',
        'indexes': [
            {
                'fields': ['chat_id'],
                'unique': True,
            },
            {
                'fields': ['participants'],
                'unique': True,
            },
        ],
    }

    def save(self, *args, **kwargs):
        if not self.chat_id:
            self.chat_id = shortuuid.uuid()
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)
