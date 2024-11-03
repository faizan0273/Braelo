'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing (Upsert) Serializers.
---------------------------------------------------
'''

from django.db import transaction
from django.utils import timezone
from azure.storage.blob import BlobServiceClient
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework_mongoengine import serializers
from helpers.constants import CATEGORIES
from helpers.listsync import ListSynchronize
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME
from listings.models import (
    ElectronicsListing,
    EventsListing,
    FashionListing,
    FurnitureListing,
    JobsListing,
    RealEstateListing,
    ServicesListing,
    SportsHobbyListing,
    VehicleListing,
    KidsListing,
)

blob_service_client = BlobServiceClient.from_connection_string(
    'DefaultEndpointsProtocol=https;AccountName=braelos3;AccountKey=ODvt'
    'b8NuHRyWRsNR54wyp2lP0a7YGlM//NnhbkQKKv+JhX9E9Z+JXUSX56/sY7q0OxYPjidA5'
    'HL0+AStWzRAYA==;EndpointSuffix=core.windows.net'
)


class Serializer(serializers.DocumentSerializer):
    class Meta:
        abstract = True

    def create(self, validated_data):
        '''
        Handle the creation of listings and picture uploads.
        This method can be extended by child classes for custom logic.
        '''
        with transaction.atomic():
            listing = self.Meta.model.objects.create(**validated_data)
            ListSynchronize.listsync(validated_data, listing.id)
        return listing

    def validate(self, data):
        '''
        Common validation logic for listings.
        Ensures category and subcategory validation and user association.
        '''
        user = self.context['request'].user
        data['user_id'] = user.id
        category = data.get('category')
        subcategory = data.get('subcategory')
        year = data.get('year')
        status = data.get('is_active')

        # Validate category and subcategory
        if category != self.Meta.category:
            raise ValidationError(
                {'category': f'categories should be {self.Meta.category}'}
            )
        if subcategory and subcategory not in CATEGORIES.get(category, []):
            raise ValidationError(
                {
                    'subcategory': f'subcategories should be {CATEGORIES[category]}'
                }
            )
        if year:
            current_year = timezone.now().year
            if year < 1886 or year > current_year:
                raise ValidationError(
                    {'year': f'Year must be between 1886 and {current_year}.'}
                )
        data['is_active'] = True if status else False
        pictures = data.pop('pictures', [])
        s3_urls = []

        for picture in pictures:
            if isinstance(picture, InMemoryUploadedFile):
                file_name = f'listings/{category}/{user.id}/{picture.name}'
                # Upload file to Azure Blob Storage
                blob_client = blob_service_client.get_blob_client(
                    container=AZURE_CONTAINER_NAME, blob=file_name
                )
                blob_client.upload_blob(picture, overwrite=True)

                # Create a URL to access the uploaded image
                picture_url = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}'
                s3_urls.append(picture_url)

        # Assign uploaded picture URLs to validated data
        data['pictures'] = s3_urls

        # Timestamps
        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        return data


class ElectronicsSerializer(Serializer):
    class Meta:
        model = ElectronicsListing
        fields = '__all__'
        category = 'Electronics'


class EventsSerializer(Serializer):
    class Meta:
        model = EventsListing
        fields = '__all__'
        category = 'Events'


class FashionSerializer(Serializer):
    class Meta:
        model = FashionListing
        fields = '__all__'
        category = 'Fashion'


class FurnitureSerializer(Serializer):
    class Meta:
        model = FurnitureListing
        fields = '__all__'
        category = 'Furniture'


class JobsSerializer(Serializer):
    class Meta:
        model = JobsListing
        fields = '__all__'
        category = 'Jobs'


class KidsSerializer(Serializer):
    class Meta:
        model = KidsListing
        fields = '__all__'
        category = 'Kids'


class RealEstateSerializer(Serializer):
    class Meta:
        model = RealEstateListing
        category = 'Real Estate'
        fields = '__all__'


class ServicesSerializer(Serializer):
    class Meta:
        model = ServicesListing
        fields = '__all__'
        category = 'Services'


class SportsHobbySerializer(Serializer):
    class Meta:
        model = SportsHobbyListing
        fields = '__all__'
        category = 'Sports & Hobby'


class VehicleSerializer(Serializer):
    class Meta:
        model = VehicleListing
        fields = '__all__'
        category = 'Vehicles'
