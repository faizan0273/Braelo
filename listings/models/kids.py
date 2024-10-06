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
    NEGOTIABLE,
    DONATION,
    CERTIFICATION,
    KIDS_GRADES,
)


class KidsListing(Document):
    '''
    Kids category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # Price-related fields
    price = fields.DecimalField(required=True)
    negotiable = fields.StringField(choices=NEGOTIABLE, required=True)

    # Donation
    donation = fields.StringField(choices=DONATION, required=True)

    # Common fields for subcategories
    age_range = fields.StringField(required=True)
    expiry_date = fields.DateTimeField(required=False)
    duration = fields.StringField(required=False)
    certification = fields.StringField(choices=CERTIFICATION, required=False)

    # Specific fields for subcategories
    # Health
    product_type = fields.StringField(required=False)
    # Toys
    toy_type = fields.StringField(required=False)
    safety_standard = fields.StringField(required=False)

    # Transport
    vehicle_type = fields.StringField(required=False)
    weight_capacity = fields.StringField(required=False)

    # Accessories Type
    accessories_type = fields.StringField(required=False)

    # Classes
    subject = fields.StringField(required=False)
    experience_level = fields.StringField(required=False)
    no_of_children = fields.IntField(required=False)

    # Schools/Daycare/Babysitter
    babysitter_experience = fields.StringField(required=False)
    grades = fields.StringField(choices=KIDS_GRADES, required=False)
    # After school program
    activities_offered = fields.StringField(required=False)
    # Activities
    activity_type = fields.StringField(required=False)
    equipment_required = fields.BooleanField(default=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'kids_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
