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


class SavedItem(Document):
    user_id = fields.IntField()
    listing_id = fields.ObjectIdField(required=True)
    category = fields.StringField(required=True)
    title = fields.StringField(required=True)
    location = fields.StringField(required=True)
    price = fields.DecimalField(required=True)
    pictures = fields.ListField(fields.StringField(), required=False)
    saved_at = fields.DateTimeField()
    created_at = fields.DateTimeField(required=True)

    # Status
    is_active = fields.BooleanField(required=True, default=True)

    meta = {
        'collection': 'saved_listings',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['listing_id']},
            {'fields': ['category']},
            {'fields': ['location']},
            {'fields': ['title']},
            {'fields': ['user_id', 'listing_id']},
        ],
    }
