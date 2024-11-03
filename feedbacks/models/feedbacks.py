'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User Feedbacks model.
---------------------------------------------------
'''

from mongoengine import Document
from mongoengine.fields import (
    IntField,
    StringField,
    DateTimeField,
)


class Feedbacks(Document):
    user_id = IntField()
    feedback = StringField(required=True)
    created_at = DateTimeField()

    meta = {
        'collection': 'feedbacks',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['created_at']},
        ],
    }
