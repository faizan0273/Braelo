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

from django.db import transaction
from django.utils import timezone
from azure.storage.blob import BlobServiceClient
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError
from listings.helpers.constants import CATEGORIES


from listings.models import (
    ElectronicsListing,
    EventsListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    FurnitureListing,
    FashionListing,
    KidsListing,
    RealEstateListing,
    VehicleListing,
    SavedItem,
)
from listings.models.listsync import ListSync
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME

blob_service_client = BlobServiceClient.from_connection_string(
    'DefaultEndpointsProtocol=https;AccountName=braelos3;AccountKey=ODvt'
    'b8NuHRyWRsNR54wyp2lP0a7YGlM//NnhbkQKKv+JhX9E9Z+JXUSX56/sY7q0OxYPjidA5'
    'HL0+AStWzRAYA==;EndpointSuffix=core.windows.net'
)


def listsync(data, _id):
    obj = {
        'user_id': data['user_id'],
        'listing_id': str(_id),
        'category': data['category'],
        'title': data['title'],
        'location': data['location'],
        'created_at': data['created_at'],
    }

    # Price range
    if data.get('salary_range'):
        obj['salary_range'] = data['salary_range']
    elif data.get('service_fee'):
        obj['price'] = data['service_fee']
    elif data.get('ticket_price'):
        obj['price'] = data['ticket_price']
    else:
        obj['price'] = data['price']

    # Pictures
    if data.get('pictures'):
        obj['pictures'] = data['pictures']

    list_sync_entry = ListSync(**obj)
    list_sync_entry.save()


class ListsyncSerializer(serializers.DocumentSerializer):
    class Meta:
        model = ListSync
        fields = '__all__'


class SavedItemSerializer(serializers.DocumentSerializer):
    class Meta:
        model = SavedItem

    def validate(self, data):
        user = self.context['request'].user
        data['user_id'] = user.id
        category = data.get('category')
        if category not in CATEGORIES:
            raise ValidationError(
                {'category': f'categories should be {CATEGORIES}'}
            )
        data['saved_at'] = timezone.now()
        return data

    def create(self, validated_data):
        return SavedItem.objects.create(**validated_data)


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
            listsync(validated_data, listing.id)
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


class VehicleSerializer(Serializer):
    class Meta:
        model = VehicleListing
        fields = '__all__'
        category = 'vehicles'


class RealEstateSerializer(Serializer):
    class Meta:
        model = RealEstateListing
        category = 'real estate'
        fields = '__all__'


class ElectronicsSerializer(Serializer):
    class Meta:
        model = ElectronicsListing
        fields = '__all__'
        category = 'electronics'


class EventsSerializer(Serializer):
    class Meta:
        model = EventsListing
        fields = '__all__'
        category = 'events'


class JobsSerializer(Serializer):
    class Meta:
        model = JobsListing
        fields = '__all__'
        category = 'jobs'


class ServicesSerializer(Serializer):
    class Meta:
        model = ServicesListing
        fields = '__all__'
        category = 'events'


class SportsHobbySerializer(Serializer):
    class Meta:
        model = SportsHobbyListing
        fields = '__all__'
        category = 'sports & hobby'


class FurnitureSerializer(Serializer):
    class Meta:
        model = FurnitureListing
        fields = '__all__'
        category = 'furniture'


class FashionSerializer(Serializer):
    class Meta:
        model = FashionListing
        fields = '__all__'
        category = 'fashion'


class KidsSerializer(Serializer):
    class Meta:
        model = KidsListing
        fields = '__all__'
        category = 'kids'
