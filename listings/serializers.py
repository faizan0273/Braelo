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

from .helpers.constants import CATEGORIES
from .models import (
    ElectronicsListing,
    EventsListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    FurnitureListing,
    FashionListing,
    KidsListing,
)
from .models.real_estate import RealEstateListing
from .models.vehicle import VehicleListing


class VehicleSerializer(serializers.DocumentSerializer):
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
        '''
        Override the create method to handle Vehicle listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = VehicleListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        year = data.get('year')
        vehicle = ('electronics', 'Electronics')
        if category not in vehicle:
            raise ValidationError(
                {'category': f'categories should be {vehicle}'}
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

        return data


class RealEstateSerializer(serializers.DocumentSerializer):
    class Meta:
        model = RealEstateListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle real estate listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = RealEstateListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
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

        return data


class ElectronicsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = ElectronicsListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle electronics creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = ElectronicsListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        electronics = ('electronics', 'Electronics')
        if category not in electronics:
            raise ValidationError(
                {'category': f'categories should be {electronics}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class EventsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = EventsListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle events listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = EventsListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        events = ('events', 'Events')
        if category not in events:
            raise ValidationError(
                {'category': f'categories should be {events}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class JobsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = JobsListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle jobs listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = JobsListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        jobs = ('jobs', 'Jobs')
        if category not in jobs:
            raise ValidationError({'category': f'categories should be {jobs}'})
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class ServicesSerializer(serializers.DocumentSerializer):
    class Meta:
        model = ServicesListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle service listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = ServicesListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        service = ('services', 'Services')
        if category not in service:
            raise ValidationError(
                {'category': f'categories should be {service}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class SportsHobbySerializer(serializers.DocumentSerializer):
    class Meta:
        model = SportsHobbyListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle sports and hobby creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = SportsHobbyListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        sport = ('sport & hobby', 'Sports & Hobby')
        if category not in sport:
            raise ValidationError({'category': f'categories should be {sport}'})
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class FurnitureSerializer(serializers.DocumentSerializer):
    class Meta:
        model = FurnitureListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle furniture listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = FurnitureListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        furniture = ('furniture', 'Furniture')
        if category not in furniture:
            raise ValidationError(
                {'category': f'categories should be {furniture}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class FashionSerializer(serializers.DocumentSerializer):
    class Meta:
        model = FashionListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle fashion Listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = FashionListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        fashion = ('fashion', 'Fashion')
        if category not in fashion:
            raise ValidationError(
                {'category': f'categories should be {fashion}'}
            )
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data


class KidsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = KidsListing
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        '''
        Override the create method to handle Kids listing creation.
        '''
        pictures = validated_data.pop('pictures', [])
        listing = KidsListing.objects.create(**validated_data)
        if pictures:
            listing.pictures = pictures

        listing.save()
        return listing

    def validate(self, data):
        category = data.get('category')
        subcategory = data.get('subcategory')
        kids = ('kids', 'Kids')
        if category not in kids:
            raise ValidationError({'category': f'categories should be {kids}'})
        if subcategory not in CATEGORIES[category]:
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        return data
