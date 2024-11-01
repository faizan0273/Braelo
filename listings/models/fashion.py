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
from listings.helpers.constants import FashionConstants as FC
from mongoengine.fields import (
    IntField,
    StringField,
    ListField,
    BooleanField,
    DateTimeField,
    DecimalField,
)


class FashionListing(Document):
    '''
    Fashion category listings.
    '''

    user_id = IntField()
    category = StringField(required=True)
    subcategory = StringField(required=True)
    pictures = ListField(required=True)
    title = StringField(required=True)
    description = StringField(required=True)
    location = StringField(required=True)

    # category based
    # fashion attributes
    brand = StringField(required=True)
    size = StringField(required=True)
    color = StringField(required=True)
    material_type = StringField(required=True)

    gender = StringField(required=False)
    # todo why two sizes
    condition = StringField(choices=FC.CONDITION, required=True)
    donation = StringField(choices=FC.DONATION, required=True)

    price = DecimalField(required=True)
    negotiable = StringField(choices=FC.NEGOTIABLE, required=True)

    # Shoes
    shoe_type = StringField(required=False)

    # Accessories
    accessories_type = StringField(required=False)

    # Beauty products
    skin_type = StringField(required=False)
    expiry_date = DateTimeField(required=False)

    # Jewelry
    metal_type = StringField(required=False)
    gem_stone = StringField(required=False)

    # Timestamps
    created_at = DateTimeField()
    updated_at = DateTimeField()

    # Status
    is_active = BooleanField(required=True, default=True)

    meta = {
        'collection': 'fashion_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
