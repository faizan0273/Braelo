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
from listings.helpers.constants import VehicleConstants


class VehicleListing(Document):
    '''
    Vehicle category listings.
    '''

    user_id = fields.IntField()
    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.StringField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    make = fields.StringField(required=True)
    model = fields.StringField(required=True)
    year = fields.IntField(required=True)
    color = fields.StringField(required=True)
    mileage = fields.IntField(required=False)
    fuel = fields.FloatField(required=False)
    price = fields.DecimalField(required=True)
    transmission = fields.StringField(
        choices=VehicleConstants.TRANSMISSION,
        required=False,
        default=None,
    )
    condition = fields.StringField(
        choices=VehicleConstants.CONDITION, required=True
    )
    number_of_doors = fields.StringField(
        choices=VehicleConstants.NUMBER_OF_DOORS, required=False
    )
    purpose = fields.StringField(
        choices=VehicleConstants.PURPOSE, required=False
    )
    negotiable = fields.StringField(
        choices=VehicleConstants.NEGOTIABLE, required=True
    )
    Load_capacity = fields.IntField(required=False)
    type = fields.IntField(required=False)
    length = fields.IntField(required=False)
    passenger_capacity = fields.IntField(required=False)
    vehicle_type = fields.StringField(required=False)
    rental_duration = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    # Status
    is_active = fields.BooleanField(required=True, default=True)

    meta = {
        'collection': 'vehicle_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
