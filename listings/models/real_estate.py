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
    CONDITION,
    BASEMENT,
    FURNISHED,
    LEASE_TERMS,
    CREDIT_SCORE_REQ,
    UTILITIES,
    AMENITIES,
    ADDITIONAL_FEES,
    PET_POLICY,
    RENTERS_INSURANCE,
    SECURITY_MEASURE,
)


class RealEstateListing(Document):
    '''
    Real Estate category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    property_type = fields.StringField(required=True)
    bedrooms = fields.IntField(min_value=0, required=True)
    bathrooms = fields.IntField(min_value=0, required=True)
    year_built = fields.IntField(min_value=1800, required=False)
    size = fields.FloatField(required=True)
    condition = fields.StringField(choices=CONDITION, required=True)
    basement = fields.StringField(choices=BASEMENT, required=False)
    furnished = fields.StringField(choices=FURNISHED, default=False)
    parking_and_cost = fields.StringField(required=False)
    lease_terms = fields.StringField(choices=LEASE_TERMS, required=False)
    maintenance_policy = fields.StringField(required=False)
    credit_score = fields.StringField(choices=CREDIT_SCORE_REQ, required=False)
    utilities_included = fields.ListField(
        fields.StringField(choices=UTILITIES), required=False
    )
    access_to_amenities = fields.ListField(
        fields.StringField(choices=AMENITIES), required=False
    )
    additional_fees = fields.StringField(
        choices=ADDITIONAL_FEES, required=False
    )
    pet_policy = fields.StringField(
        choices=PET_POLICY,
        required=False,
    )
    renters_insurance_requirement = fields.StringField(
        choices=RENTERS_INSURANCE, default=False
    )
    security_measures = fields.ListField(
        fields.StringField(choices=SECURITY_MEASURE),
        required=False,
    )
    other = fields.StringField(required=False)
    lease_managed_by = fields.StringField(choices=LEASE_TERMS, required=False)
    price = fields.FloatField(required=True)
    negotiable = fields.ListField(max_length=2, required=False, default=None)
    land_type = fields.StringField(required=False)
    number_of_floors = fields.IntField(min_value=0)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'real_estate_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
