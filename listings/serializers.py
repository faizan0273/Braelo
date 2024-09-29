'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for Listings based endpoints
---------------------------------------------------
'''

from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_mongoengine import serializers

from .helpers.constants import (
    CATEGORIES,
    TRANSMISSION,
    CONDITION,
    NUMBER_OF_DOORS,
    PURPOSE,
    NEGOTIABLE,
    FOR_SALE,
)
from .models import Listing
from .models.real_estate import RealEstateListing
from .models.vehicle import VehicleListing


class ListingSerializer(serializers.DocumentSerializer):

    class Meta:
        model = Listing
        fields = [
            'id',
            'category',
            'subcategory',
            'pictures',
            'title',
            'description',
            'location',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        '''
        Validate that the email exists in the database.
        '''
        return data

    def create(self, validated_data):
        '''
        Create a new listing instance with multiple images.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = Listing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures
            listing.save()
        listing.save()
        return listing


class VehicleListingSerializer(serializers.DocumentSerializer):
    class Meta:
        model = VehicleListing
        fields = [
            'id',
            'category',
            'subcategory',
            'pictures',
            'title',
            'description',
            'location',
            'make',
            'model',
            'year',
            'color',
            'mileage',
            'fuel',
            'price',
            'transmission',
            'condition',
            'number_of_doors',
            'purpose',
            'negotiable',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Override the create method to handle VehicleListing creation.
        """
        pictures = validated_data.pop('pictures', [])
        vehicle_listing = VehicleListing.objects.create(**validated_data)
        if pictures:
            vehicle_listing.pictures = pictures

        vehicle_listing.save()
        return vehicle_listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        year = data.get('year')
        optionals = {
            'transmission': TRANSMISSION,
            'condition': CONDITION,
            'number_of_doors': NUMBER_OF_DOORS,
            'purpose': PURPOSE,
            'negotiable': NEGOTIABLE,
            'for_sale': FOR_SALE,
        }

        if category not in CATEGORIES:
            raise ValidationError(
                {'category': f'categories should be {CATEGORIES.keys()}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        current_year = timezone.now().year
        if year < 1886 or year > current_year:
            raise ValidationError(
                {'year': f'Year must be between 1886 and {current_year}.'}
            )
        for field, options in optionals.items():
            val = data.get(field)
            if val and val not in options:
                raise ValidationError(
                    {field: f'{field} should be in {options}'}
                )
        return data


class RealEstateListingSerializer(serializers.DocumentSerializer):
    class Meta:
        model = RealEstateListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Override the create method to handle VehicleListing creation.
        """
        pictures = validated_data.pop('pictures', [])
        real_estate_listing = RealEstateListing.objects.create(**validated_data)
        if pictures:
            real_estate_listing.pictures = pictures

        real_estate_listing.save()
        return real_estate_listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        # year = data.get('year')

        if category not in CATEGORIES:
            raise ValidationError(
                {'category': f'categories should be {CATEGORIES.keys()}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        # current_year = timezone.now().year
        # if year < 1886 or year > current_year:
        #     raise ValidationError(
        #         {'year': f'Year must be between 1886 and {current_year}.'}
        #     )

        return data
