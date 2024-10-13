'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for Listings based endpoints
---------------------------------------------------
'''

from mongoengine import Document, fields

from django.utils import timezone


class SavedItem(Document):
    user_id = fields.IntField(required=True)
    listing = fields.DictField(required=True)
    created_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'saved_listings',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['listing']},
            {'fields': ['user_id', 'listing']},
        ],
    }
