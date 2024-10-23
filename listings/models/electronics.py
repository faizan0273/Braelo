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
from listings.helpers.constants import ElectronicsConstants


class ElectronicsListing(Document):
    '''
    Electronics category listings.
    '''

    user_id = fields.IntField()
    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.StringField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    brand = fields.StringField(required=True)
    model = fields.StringField(required=True)
    warranty = fields.StringField(required=True)
    operating_system = fields.StringField(required=False)
    carrier_lock = fields.StringField(required=False)
    condition = fields.StringField(
        choices=ElectronicsConstants.CONDITION, required=True
    )
    price = fields.DecimalField(required=True)
    negotiable = fields.StringField(
        choices=ElectronicsConstants.NEGOTIABLE, required=True
    )

    # Computer
    processor = fields.StringField(required=False)
    ram = fields.StringField(required=False)
    storage_type = fields.StringField(required=False)

    # Appliances
    energy_rating = fields.StringField(required=False)
    dimension = fields.StringField(required=False)

    # Games
    platforms = fields.StringField(required=False)
    jenry = fields.StringField(required=False)

    # Services and parts
    part_type = fields.StringField(required=False)
    compatible_model = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    # Status
    is_active = fields.BooleanField(required=True, default=True)

    meta = {
        'collection': 'electronics_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
