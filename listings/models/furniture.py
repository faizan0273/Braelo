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
from listings.helpers.constants import FurnitureConstants


class FurnitureListing(Document):
    '''
    Furniture category listings.
    '''

    user_id = fields.IntField()
    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.StringField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    material_type = fields.StringField(required=True)
    color = fields.StringField(required=True)
    dimensions = fields.StringField(required=True)
    seating_capacity = fields.StringField(required=False)

    upholstery_material = fields.StringField(required=False)
    condition = fields.StringField(
        choices=FurnitureConstants.CONDITION, required=True
    )
    donation = fields.StringField(
        choices=FurnitureConstants.DONATION, required=True
    )

    price = fields.DecimalField(required=True)
    negotiable = fields.StringField(
        choices=FurnitureConstants.NEGOTIABLE, required=True
    )

    # Tables
    table_type = fields.StringField(required=False)
    shapes = fields.StringField(required=False)

    # Chairs
    chair_type = fields.StringField(required=False)
    weight_capacity = fields.StringField(required=False)

    # Bed
    bed_size = fields.StringField(required=False)
    mattress_included = fields.StringField(
        choices=FurnitureConstants.MATTRESS_INCLUDED, required=False
    )

    # Custom furniture
    customization = fields.StringField(required=False)
    lead_time = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    meta = {
        'collection': 'furniture_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
