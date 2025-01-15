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
            file_name = (
                f'business_listings/{business_type}/{user.id}/{picture.name}'
            )
            blob_client = blob_service_client.get_blob_client(
                container=AZURE_CONTAINER_NAME, blob=file_name
            )
            blob_client.upload_blob(picture, overwrite=True)

            picture_url = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}'
            s3_urls.append(picture_url)

        return s3_urls

    def create(self, validated_data):
        '''
        handles the creation of business after validating pictures
        '''
        user = self.context['request'].user
        business_category = validated_data.get('business_category')
        bussines_logo = validated_data.get('business_logo', [])
        business_images = validated_data.get('business_images', [])
        # Upload Logo
        s3_logo_url = self.upload_pictures(
            bussines_logo, business_category, user
        )
        # Upload Business Images
        s3_image_urls = self.upload_pictures(
            business_images, business_category, user
        )
        # Add Urls to valdiated Fields
        validated_data['business_logo'] = s3_logo_url
        validated_data['business_images'] = s3_image_urls

        listing = Business.objects.create(**validated_data)
        user.is_business = True
        user.save()
        return listing

    def update(self, instance, validated_data):
        '''
        Handle the update of listings and related fields.
        This method can be extended by child classes for custom logic.
        '''
        business_logo = validated_data.pop('business_logo', None)
        user = self.context['request'].user
        if business_logo:
            # Delete already existed ones
            if instance.business_logo:
                for picture_url in instance.business_logo:
                    # Extract the blob name from the URL
                    blob_name = picture_url.split(f'{AZURE_CONTAINER_NAME}/')[
                        -1
                    ]
                    blob_client = blob_service_client.get_blob_client(
                        container=AZURE_CONTAINER_NAME, blob=blob_name
                    )
                    blob_client.delete_blob()
                    # Upload New ones
            s3_urls = self.upload_pictures(
                business_logo, instance.business_category, user
            )

            # Replace existing picture URLs
            validated_data['business_logo'] = s3_urls

        business_images = validated_data.pop('business_images', None)
        user = self.context['request'].user
        if business_images:
            # Delete already existed ones
            if instance.business_images:
                for picture_url in instance.business_images:
                    # Extract the blob name from the URL
                    blob_name = picture_url.split(f'{AZURE_CONTAINER_NAME}/')[
                        -1
                    ]
                    blob_client = blob_service_client.get_blob_client(
                        container=AZURE_CONTAINER_NAME, blob=blob_name
                    )
                    blob_client.delete_blob()
                    # Upload New ones
            s3_urls = self.upload_pictures(
                business_images, instance.business_category, user
            )

            # Replace existing picture URLs
            validated_data['business_images'] = s3_urls

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
        business_images = data.get('business_images', [])

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
        _validate_email(business_email, 'Enter a valid business email address')
        validate_phone(business_number)
        validate_image(business_logo, 'Logo')
        validate_image(business_images, 'Images')

        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        data['is_active'] = True

        return data
