'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Business Listing model mongo based.
---------------------------------------------------
'''

from mongoengine import Document
from mongoengine.fields import (
    IntField,
    StringField,
    ListField,
    BooleanField,
    DateTimeField,
    EmailField,
    PointField,
)
from rest_framework.exceptions import ValidationError


class Business(Document):
    '''
    business listings model
    '''

    user_id = IntField(required=False)
    business_name = StringField(required=True)
    business_logo = ListField(required=True)
    business_banner = ListField(required=True)
    business_address = StringField(required=True)
    business_coordinates = PointField(required=True)
    business_website = StringField(required=False)
    business_number = StringField(required=True)
    business_email = EmailField(required=True)
    business_category = StringField(required=True)
    business_subcategory = StringField(required=True)
    business_images = ListField(required=True)
    business_goals = StringField(required=False)
    business_qr = ListField(required=False)
    business_url = StringField(required=False)
    is_active = BooleanField(required=True, default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        'collection': 'business_listings',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['business_name']},
            {'fields': ['business_category']},
            {'fields': ['business_subcategory']},
            {'fields': ['business_coordinates'], 'types': '2dsphere'},
        ],
    }

    # def Validate_coordinates(self):
    #     '''
    #     Custom validation to ensure business_coordinates contains [longitude, latitude]
    #     '''
    #     coords = self.business_coordinates.get('coordinates')

    #     if not isinstance(coords, list) or len(coords) != 2:
    #         raise ValidationError(
    #             'business_coordinates must be a list with [longitude, latitude].'
    #         )

    #     lon, lat = coords
    #     if not (
    #         isinstance(lon, (int, float)) and isinstance(lat, (int, float))
    #     ):
    #         raise ValidationError('Longitude and latitude must be numbers.')

    #     # Ensure values are within valid longitude/latitude range
    #     if not (-180 <= lon <= 180 and -90 <= lat <= 90):
    #         raise ValidationError(
    #             'Longitude must be between -180 and 180, latitude must be between -90 and 90.'
    #         )
