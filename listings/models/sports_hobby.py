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

from mongoengine import fields, Document
from listings.helpers.constants import SportsHobbyConstants


class SportsHobbyListing(Document):
    '''
    Sports & Hobby category listings.
    '''

    user_id = fields.IntField()
    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.StringField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # Specific fields for Sports & Hobby
    item_type = fields.StringField(required=True)
    condition = fields.StringField(
        choices=SportsHobbyConstants.CONDITION, required=True
    )
    activity_type = fields.StringField(required=False)

    # Pricing and Negotiation
    price = fields.DecimalField(required=True)
    negotiable = fields.StringField(
        choices=SportsHobbyConstants.NEGOTIABLE, required=True
    )

    # Timestamps
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

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
