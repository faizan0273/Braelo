from django.utils import timezone
from azure.storage.blob import BlobServiceClient
from rest_framework.exceptions import ValidationError
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME
from django.core.files.uploadedfile import InMemoryUploadedFile


import phonenumbers
from rest_framework_mongoengine import serializers
from django.core.validators import validate_email
from users.models.business import Business
from helpers.constants import BUSINESS_TYPE


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
            raise ValidationError({'error':'This is not valid phone number.'})
     except phonenumbers.NumberParseException:
        raise ValidationError({'error':'This is not valid phone number.'})



def validate_image(file, picture):
    if isinstance(file, InMemoryUploadedFile):
        if not file.name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError({picture: f'Invalid {picture} format'})


class BusinessSerailizer(serializers.DocumentSerializer):

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
        user = self.context['request'].user
        business_type = validated_data.get('business_type')
        bussines_logo = validated_data.get('business_logo', [])
        business_images = validated_data.get('business_images', [])
        # Upload Logo
        s3_logo_url = self.upload_pictures(bussines_logo, business_type, user)
        # Upload Business Images
        s3_image_urls = self.upload_pictures(
            business_images, business_type, user
        )
        # Add Urls to valdiated Fields
        validated_data['business_logo'] = s3_logo_url
        validated_data['business_images'] = s3_image_urls

        listing = Business.objects.create(**validated_data)
        return listing

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_business:
            raise ValidationError(
                {'User':'Not Business User'}
            )
        data['user_id'] = user.id
        owner_email = data.get('owner_email')
        business_email = data.get('business_email')
        owner_phone = data.get('owner_phone')
        business_number = data.get('business_number')
        business_type = data.get('business_type')
        business_logo = data.get('business_logo', [])
        business_images = data.get('business_images', [])

        # validation checks for various fields
        _validate_email(owner_email, 'Enter a valid owner email address')
        _validate_email(business_email, 'Enter a valid business email address')
        validate_phone(owner_phone)
        validate_phone(business_number)
        if business_type not in BUSINESS_TYPE:
            raise ValidationError(
                {'Business Type': f'Type must be in {BUSINESS_TYPE}.'}
            )
        validate_image(business_logo, 'Logo')
        validate_image(business_images, 'Images')

        data['created_at'] = timezone.now()
        data['is_active'] = True

        return data
