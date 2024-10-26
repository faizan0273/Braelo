'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Vehicle Listing model mongo based.
---------------------------------------------------
'''

from mongoengine import Document
from listings.helpers.constants import SportsHobbyConstants as SHC
from mongoengine.fields import (
    IntField,
    StringField,
    ListField,
    BooleanField,
    DateTimeField,
    DecimalField,
)


class SportsHobbyListing(Document):
    '''
    Sports & Hobby category listings.
    '''

    user_id = IntField()
    category = StringField(required=True)
    subcategory = StringField(required=True)
    pictures = ListField(required=True)
    title = StringField(required=True)
    description = StringField(required=True)
    location = StringField(required=True)

    # Specific fields for Sports & Hobby
    item_type = StringField(required=True)
    condition = StringField(choices=SHC.CONDITION, required=True)
    activity_type = StringField(required=False)

    # Pricing and Negotiation
    price = DecimalField(required=True)
    negotiable = StringField(choices=SHC.NEGOTIABLE, required=True)

    # Timestamps
    created_at = DateTimeField()
    updated_at = DateTimeField()

    # Status
    is_active = BooleanField(required=True, default=True)

    meta = {
        'collection': 'sports_hobby_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
