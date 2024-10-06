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

from django.utils import timezone
from mongoengine import fields, Document

from ..helpers.constants import CONDITION, DONATION, NEGOTIABLE


class FashionListing(Document):
    '''
    Fashion category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    # fashion attributes
    brand = fields.StringField(required=True)
    size = fields.StringField(required=True)
    color = fields.StringField(required=True)
    material_type = fields.StringField(required=True)

    gender = fields.StringField(required=False)
    # todo why two sizes
    condition = fields.StringField(choices=CONDITION, required=True)
    donation = fields.StringField(choices=DONATION, required=True)

    price = fields.DecimalField(required=True)
    negotiable = fields.StringField(choices=NEGOTIABLE, required=True)

    # Shoes
    shoe_type = fields.StringField(required=False)

    # Accessories
    accessories_type = fields.StringField(required=False)

    # Beauty products
    skin_type = fields.StringField(required=False)
    expiry_date = fields.DateTimeField(required=False)

    # Jewelry
    metal_type = fields.StringField(required=False)
    gem_stone = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

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
