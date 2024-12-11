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

from mongoengine import Document
from mongoengine.fields import (
    IntField,
    StringField,
    ListField,
    BooleanField,
    DateTimeField,
    DecimalField,
    ObjectIdField,
)


class ListSync(Document):
    user_id = IntField(required=True)
    listing_id = ObjectIdField(required=True)
    category = StringField(required=True)
    subcategory = StringField(required=True)
    title = StringField(required=True)
    keywords = ListField(StringField(required=True), required=True)
    location = StringField(required=True)
    price = DecimalField(required=False)
    salary_range = StringField(required=False)
    pictures = ListField(required=True)
    created_at = DateTimeField()

    # Status
    is_active = BooleanField(required=True, default=True)

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
