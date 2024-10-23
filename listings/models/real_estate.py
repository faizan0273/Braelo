"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Vehicle Listing model mongo based.
---------------------------------------------------
"""

from mongoengine import fields, Document
from listings.helpers.constants import RealEstateConstants


class RealEstateListing(Document):
    """
    Real Estate category listings.
    """

    user_id = fields.IntField()
    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    property_type = fields.StringField(required=True)
    bedrooms = fields.IntField(min_value=0, required=True)
    bathrooms = fields.IntField(min_value=0, required=True)
    year_built = fields.IntField(min_value=1800, required=False)
    size = fields.FloatField(required=True)
    condition = fields.StringField(choices=RealEstateConstants.CONDITION, required=True)
    basement = fields.StringField(choices=RealEstateConstants.BASEMENT, required=False)
    furnished = fields.StringField(choices=RealEstateConstants.FURNISHED, default=False)
    parking_and_cost = fields.StringField(required=False)
    lease_terms = fields.StringField(
        choices=RealEstateConstants.LEASE_TERMS, required=False
    )
    maintenance_policy = fields.StringField(required=False)
    credit_score = fields.StringField(
        choices=RealEstateConstants.CREDIT_SCORE_REQ, required=False
    )
    utilities_included = fields.ListField(
        fields.StringField(choices=RealEstateConstants.UTILITIES),
        required=False,
    )
    access_to_amenities = fields.ListField(
        fields.StringField(choices=RealEstateConstants.AMENITIES),
        required=False,
    )
    additional_fees = fields.StringField(
        choices=RealEstateConstants.ADDITIONAL_FEES, required=False
    )
    pet_policy = fields.StringField(
        choices=RealEstateConstants.PET_POLICY,
        required=False,
    )
    renters_insurance_requirement = fields.StringField(
        choices=RealEstateConstants.RENTERS_INSURANCE, default=False, required=False
    )
    security_measures = fields.ListField(
        fields.StringField(choices=RealEstateConstants.SECURITY_MEASURE),
        required=False,  # error here
    )
    other = fields.StringField(required=False)
    lease_managed_by = fields.StringField(
        choices=RealEstateConstants.LEASE_TERMS, required=False
    )
    price = fields.FloatField(required=True)
    negotiable = fields.StringField(
        choices=RealEstateConstants.NEGOTIABLE, required=True
    )
    land_type = fields.StringField(required=False)
    number_of_floors = fields.IntField(min_value=0)
    bathroom_type = fields.StringField(
        choices=RealEstateConstants.BATHROOM_TYPE, required=False
    )
    kitchen_access_type = fields.StringField(
        choice=RealEstateConstants.KITCHEN_ACCESS_TYPE, required=False
    )
    laundry_facilities = fields.StringField(
        choices=RealEstateConstants.LAUNDRY_FACILITIES, required=False
    )
    smoking_policy = fields.StringField(
        choices=RealEstateConstants.SMOKING_POLICY, required=False
    )
    security_features = fields.StringField(
        choices=RealEstateConstants.SECURITY_FEATURES, required=False
    )
    preferred_occupants = fields.StringField(
        choices=RealEstateConstants.PREFERRED_OCCUPANTS, required=False
    )


    # Timestamps
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    # Status
    is_active = fields.BooleanField(required=True, default=True)

    meta = {
        "collection": "real_estate_listing",
        "ordering": ["-created_at"],
        "indexes": [
            {"fields": ["title"]},
            {"fields": ["location"]},
            {"fields": ["category"]},
            {"fields": ["subcategory"]},
        ],
    }
