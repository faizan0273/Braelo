'''
---------------------------------------------------
Project:        Braelo
Date:           Dec 20, 2024
Author:         Faizan
---------------------------------------------------

Description:
Fetch Business  endpoints.
---------------------------------------------------
'''

from rest_framework import status
from mongoengine.errors import DoesNotExist
from rest_framework_mongoengine import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)


import qrcode
from io import BytesIO
from helpers import ListSync
from bson import ObjectId
from users.models.business import Business
from helpers import response, handle_exceptions
from azure.storage.blob import BlobServiceClient
from listings.serializers import ListsyncSerializer
from listings.api.paginate_listing import Pagination
from helpers.notifications import BUSSINESS_EVENT_DATA
from users.serializers.business import BusinessSerailizer
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME
from notifications.serializers.events import EventNotificationSerializer


blob_service_client = BlobServiceClient.from_connection_string(
    'DefaultEndpointsProtocol=https;AccountName=braelos3;AccountKey=ODvt'
    'b8NuHRyWRsNR54wyp2lP0a7YGlM//NnhbkQKKv+JhX9E9Z+JXUSX56/sY7q0OxYPjidA5'
    'HL0+AStWzRAYA==;EndpointSuffix=core.windows.net'
)


def generate_QR(business_id, user_id, business_type):
    '''
    Generating QR based on barelo url along with business id
    converts img object into .png format
    '''
    base_url = 'braelo-fug5gcb6c0hpbpdn.canadacentral-01.azurewebsites.net'
    business_url = f'{base_url}/auth/business/{business_id}'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(business_url)
    qr.make(fit=True)
    generate_img = qr.make_image(fill_color="black", back_color="white")
    img_byte_array = BytesIO()
    generate_img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    uploade_image = upload_pictures(img_byte_array, business_type, user_id)
    data = {
        'qr_image': uploade_image,
        'unique_url': business_url,
    }
    return data


def upload_pictures(pictures, business_type, user_id):
    '''
    Handles the uploading of pictures to Azure Blob Storage.
    Returns a list of URLs for the uploaded pictures.
    '''
    s3_urls = []
    file_name = f'business_qr/{business_type}/{user_id}.png'
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=file_name
    )
    blob_client.upload_blob(pictures, overwrite=True)

    picture_url = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}'
    s3_urls.append(picture_url)

    return s3_urls


class BussinessListing(generics.CreateAPIView):
    '''
    API endpoint to handle business creation
    '''

    queryset = Business.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessSerailizer

    @handle_exceptions
    def post(self, request):
        '''
        POST method to Creates a business listing with a unique QR code and URL.
        :param request: request object. (dict)
        :return: Business listings data. (json)
        '''
        if Business.objects(user_id=request.user.id).first():
            raise ValidationError({'Business': 'Already exists for user'})

        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        business_qr = generate_QR(
            str(instance.id),
            instance.user_id,
            instance.business_type,
        )
        instance.business_qr = business_qr.get('qr_image')
        instance.business_url = business_qr.get('unique_url')
        user = request.user
        user.previous_business = True
        instance.save()
        user.save()
        serialized_data = BusinessSerailizer(instance).data
        BUSSINESS_EVENT_DATA['data']['business_id'] = serialized_data['id']
        BUSSINESS_EVENT_DATA['data']['business_type'] = serialized_data[
            'business_type'
        ]
        BUSSINESS_EVENT_DATA['data']['user_id'] = serialized_data['user_id']
        BUSSINESS_EVENT_DATA['user_id'] = [serialized_data['user_id']]
        try:
            event_serializer = EventNotificationSerializer(
                data=BUSSINESS_EVENT_DATA
            )
            event_serializer.is_valid(raise_exception=True)
            event_serializer.save()
        except Exception:
            pass

        return response(
            status=status.HTTP_201_CREATED,
            message='Business created successfully',
            data=serialized_data,
        )


class FetchBusinesses(generics.ListAPIView):
    '''
    Fetch all business from collection
    returns data in pagination format
    '''

    queryset = Business.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = Pagination
    serializer_class = BusinessSerailizer


class ScanBusinessQR(generics.ListAPIView):
    '''
    Get endpoint to fetch business data
    will work when QR is scanned
    '''

    permission_classes = [AllowAny]

    @handle_exceptions
    def get(self, request, **kwargs):
        '''
        GET method to trigger QR code.
        :param : Primary Key. (Int)
        :return: business data. (json)
        '''

        business_id = self.kwargs['pk']
        business_listing = (
            Business.objects(id=business_id)
            .only(
                'business_logo',
                'business_name',
                'business_address',
                'business_number',
                'business_images',
            )
            .first()
        )

        if not business_listing:
            raise ValidationError({'error': 'No Business Found'})

        business_data = business_listing.to_mongo().to_dict()
        business_data.pop('_id', None)
        business_data.pop('business_qr', None)

        return response(
            status=status.HTTP_200_OK,
            message='Business Found',
            data=business_data,
        )


class DeactivateBusiness(generics.CreateAPIView):
    '''
    API endpoint to deactive a user
    '''

    permission_classes = [IsAuthenticated]

    def post(self, request):
        '''
        POST method to Deactivate business.
        :param request : reuqest object. (dict)
        :return: Deactivation Message. (json)
        '''
        try:
            user = request.user
            user_id = user.id

            if not user.is_business:
                raise ValidationError({'user': 'User Must be business'})
            business_status = Business.objects.get(
            user_id=user_id
            )
            if not business_status.is_active:
                raise ValidationError({'Business':'business is already deactivated'}) 
            business_status.is_active = False
            business_status.save()
            return response(
                status=status.HTTP_204_NO_CONTENT,
                message='Business Deleted Successfully',
                data={},
            )
        except DoesNotExist:
            raise ValidationError({'Business': 'Business not found'})


class FetchListings(generics.ListAPIView):
    '''
    Fetch user listings created from his business acc.
    '''

    queryset = ListSync.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    serializer_class = ListsyncSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_business:
            raise ValidationError('User must be business')
        try:
            queryset = ListSync.objects.filter(
                user_id=user.id, from_business=True
            )
            return queryset
        except Exception as exc:
            raise ValidationError(
                {'ListSync': f'Error retrieving data: {str(exc)}'}
            )


class UpdateBusiness(generics.UpdateAPIView):
    '''
    Base API endpoint to update a listing.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = BusinessSerailizer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        PUT method to update a listing.
        :param request: request object. (dict)
        :return: updated listing status. (json)
        '''
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        # Validate and update the business if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message='Business updated successfully',
            data=serializer.data,
        )

    def get_object(self):
        '''
        Override to fetch an object using a MongoDB ObjectId.
        '''
        pk = self.kwargs['pk']
        if not ObjectId.is_valid(pk):
            raise ValidationError({'pk': 'Invalid ObjectId format.'})
        try:
            return Business.objects.get(id=ObjectId(pk))
        except DoesNotExist:
            raise ValidationError({'detail': 'Business not found.'})


class Activate_Business(generics.UpdateAPIView):
    '''
    Business API endpoint to activate a business
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request):
        '''
        POST method to Activate a Business.
        :return: Business Active Message
        '''

        user = request.user
        user_id = user.id
        business_status = Business.objects.filter(user_id=user_id).first()
        if business_status.is_active:
            raise ValidationError({'Business': 'Business is already active'})
        business_status.is_active = True
        user.is_business = True
        business_status.save()
        user.save()

        return response(
            status=status.HTTP_201_CREATED,
            message='Business is now active',
            data={},
        )
