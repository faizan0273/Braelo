'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notification model.
---------------------------------------------------
'''

from mongoengine import (
    Document,
    StringField,
    DictField,
    BooleanField,
    DateTimeField,
    IntField,
    ListField,
)
from django.utils import timezone


class Notification(Document):
    user_id = ListField(IntField(), required=True)
    type = StringField(choices=['admin', 'chat'], required=True)
    title = StringField(required=True)
    body = StringField(required=True)
    data = DictField(required=True)
    is_read = BooleanField(default=False)
    sent = BooleanField(default=False)
    sent_at = DateTimeField()
    created_at = DateTimeField(default=timezone.now())

    meta = {
        'collection': 'notifications',
        'ordering': ['-created_at'],
        'indexes': [
            'user_id',
            'type',
            'is_read',
        ],
    }

    def mark_as_sent(self):
        self.sent = True
        self.sent_at = timezone.now()
        self.save()

    def mark_as_read(self):
        '''
        Mark notification as read.
        '''
        self.is_read = True
        self.save()
