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

from ..helpers.constants import (
    TRANSMISSION,
    CONDITION,
    NUMBER_OF_DOORS,
    PURPOSE,
    NEGOTIABLE,
)


class VehicleListing(Document):
    '''
    Vehicle category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
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
        choices=TRANSMISSION, required=False, default=None
    )
    condition = fields.ListField(choices=CONDITION, max_length=2, default=None)
    number_of_doors = fields.StringField(
        choices=NUMBER_OF_DOORS, required=False, default=None
    )
    purpose = fields.StringField(choices=PURPOSE, required=False, default=None)
    negotiable = fields.StringField(
        choices=NEGOTIABLE, required=False, default=None
    )
    Load_capacity = fields.IntField(required=False)
    type = fields.IntField(required=False)
    length = fields.IntField(required=False)
    passenger_capacity = fields.IntField(required=False)
    vehicle_type = fields.StringField(required=False)
    rental_duration = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

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
