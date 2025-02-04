'''
---------------------------------------------------
Project:        Braelo
Date:           Dec 20, 2024
Author:         Faizan
---------------------------------------------------

Description:
Fetch Business Serializers.
---------------------------------------------------
'''

import json
import uuid
from django.utils import timezone
from azure.storage.blob import BlobServiceClient
from rest_framework.exceptions import ValidationError
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME
from django.core.files.uploadedfile import InMemoryUploadedFile


import phonenumbers
from rest_framework_mongoengine import serializers
from django.core.validators import validate_email
from users.models.business import Business
from helpers.constants import CATEGORIES


blob_service_client = BlobServiceClient.from_connection_string(
    'DefaultEndpointsProtocol=https;AccountName=braelos3;AccountKey=ODvt'
    'b8NuHRyWRsNR54wyp2lP0a7YGlM//NnhbkQKKv+JhX9E9Z+JXUSX56/sY7q0OxYPjidA5'
    'HL0+AStWzRAYA==;EndpointSuffix=core.windows.net'
)


def _validate_email(email, error_message):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError({'email': error_message})


def validate_phone(phone):
    try:
        # Parsing phone number
        parsed_number = phonenumbers.parse(phone, None)
        # Checking if the parsed number is a valid number
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError({'error': 'This is not valid phone number.'})
    except phonenumbers.NumberParseException:
        raise ValidationError({'error': 'This is not valid phone number.'})


def validate_image(file, picture):
    # validate image to be in correct format for saving
    if isinstance(file, InMemoryUploadedFile):
        if not file.name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError({picture: f'Invalid {picture} format'})


class BusinessSerailizer(serializers.DocumentSerializer):
    '''
    Serailizer for business listings
    '''

    class Meta:
        model = Business
        fields = '__all__'

    def upload_pictures(self, pictures, business_type, user):
        '''
        Handles the uploading of pictures to Azure Blob Storage.
        Returns a list of URLs for the uploaded pictures.
        '''
        s3_urls = []
        for picture in pictures:
            unique_name = f"{uuid.uuid4()}_{picture.name}"
            file_name = (
                f'business_listings/{business_type}/{user.id}/{unique_name}'
            )
            blob_client = blob_service_client.get_blob_client(
                container=AZURE_CONTAINER_NAME, blob=file_name
            )
            blob_client.upload_blob(picture, overwrite=True)

            picture_url = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}'
            s3_urls.append(picture_url)

        return s3_urls

    def update_media(self, instance, business_type, business_media, user):

        # Delete already existed ones
        for picture_url in instance:
            # Extract the blob name from the URL
            blob_name = picture_url.split(f'/{AZURE_CONTAINER_NAME}/')[-1]
            blob_client = blob_service_client.get_blob_client(
                container=AZURE_CONTAINER_NAME, blob=blob_name
            )
            blob_client.delete_blob()
            # Upload New ones
        s3_urls = self.upload_pictures(
            business_media,
            business_type,
            user,
        )
        return s3_urls

    def create(self, validated_data):
        '''
        handles the creation of business after validating pictures
        '''
        user = self.context['request'].user
        business_category = validated_data.get('business_category')
        bussines_logo = validated_data.get('business_logo', [])
        business_images = validated_data.get('business_images', [])
        business_banner = validated_data.get('business_banner', [])

        # Upload Logo
        s3_logo_url = self.upload_pictures(
            bussines_logo, business_category, user
        )
        # Upload Business Images
        s3_image_urls = self.upload_pictures(
            business_images, business_category, user
        )
        # Upload banner
        s3_banner_urls = self.upload_pictures(
            business_banner, business_category, user
        )
        # Add Urls to valdiated Fields
        validated_data['business_logo'] = s3_logo_url
        validated_data['business_images'] = s3_image_urls
        validated_data['business_banner'] = s3_banner_urls

        listing = Business.objects.create(**validated_data)
        # updating fields so normal user can become business user
        user.is_business = True
        user.previous_business = True
        user.save()
        return listing

    def update(self, instance, validated_data):
        '''
        Handle the update of listings and related fields.
        This method can be extended by child classes for custom logic.
        '''
        user = self.context['request'].user
        business_logo = validated_data.pop('business_logo', None)
        business_images = validated_data.pop('business_images', None)
        business_banner = validated_data.pop('business_banner', None)

        validated_data['business_logo'] = self.update_media(
            instance.business_logo,
            instance.business_category,
            business_logo,
            user,
        )
        validated_data['business_images'] = self.update_media(
            instance.business_images,
            instance.business_category,
            business_images,
            user,
        )
        validated_data['business_banner'] = self.update_media(
            instance.business_banner,
            instance.business_category,
            business_banner,
            user,
        )

        # Update other fields
        for attr, value in validated_data.items():
            current_value = getattr(instance, attr, None)
            if current_value != value:
                setattr(instance, attr, value)

        # Update timestamps
        instance.updated_at = timezone.now()
        instance.save()
        return instance

    def validate(self, data):
        user = self.context['request'].user
        data['user_id'] = user.id
        business_email = data.get('business_email')
        business_number = data.get('business_number')
        business_category = data.get('business_category')
        business_subcategory = data.get('business_subcategory')
        business_logo = data.get('business_logo', [])
        business_banner = data.get('business_banner', [])
        business_images = data.get('business_images', [])
        business_coordinates = data.get('business_coordinates')

        # validation checks for various fields of business
        if business_category not in CATEGORIES:
            raise ValidationError(
                {'Business category': f'Type must be in {list(CATEGORIES)}.'}
            )
        if business_subcategory not in CATEGORIES.get(business_category, []):
            raise ValidationError(
                {
                    'Business subcategory': f'Type must be in {CATEGORIES[business_category]}.'
                }
            )

        if (
            not isinstance(business_coordinates, list)
            or len(business_coordinates) != 2
        ):
            raise ValidationError(
                {
                    'business_coordinates': 'business_coordinates must be a list with [longitude, latitude].'
                }
            )
        lon, lat = business_coordinates
        if not (
            isinstance(lon, (int, float)) and isinstance(lat, (int, float))
        ):
            raise ValidationError(
                {
                    'business_coordinates': 'Longitude and latitude must be numbers.'
                }
            )

        # Ensure values are within valid longitude/latitude range
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValidationError(
                {
                    'business_coordinates': 'Longitude must be between -180 and 180, latitude must be between -90 and 90.'
                }
            )

        _validate_email(business_email, 'Enter a valid business email address')
        validate_phone(business_number)
        validate_image(business_logo, 'Logo')
        validate_image(business_images, 'Images')
        validate_image(business_banner, 'Banner')

        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        data['is_active'] = True

        return data
