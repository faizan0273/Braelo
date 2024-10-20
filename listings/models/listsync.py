'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listings synchronization based endpoints.
---------------------------------------------------
'''

from mongoengine import Document, fields


class ListSync(Document):
    user_id = fields.IntField(required=True)
    listing_id = fields.ObjectIdField(required=True)
    category = fields.StringField(required=True)
    title = fields.StringField(required=True)
    location = fields.StringField(required=True)
    price = fields.DecimalField(required=False)
    salary_range = fields.StringField(required=False)
    pictures = fields.ListField(fields.StringField(), required=False)
    created_at = fields.DateTimeField()

    meta = {
        'collection': 'listsync',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['listing_id']},
            {'fields': ['category']},
            {'fields': ['location']},
            {'fields': ['title']},
            # {'fields': ['user_id', 'listing_id']},
        ],
    }
