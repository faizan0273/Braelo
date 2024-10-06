'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_mongoengine import generics

from ..models import (
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
)
from ..models.real_estate import RealEstateListing
from ..models.vehicle import VehicleListing
from ..helpers import response, handle_exceptions
from ..serializers import (
    RealEstateSerializer,
    ElectronicsSerializer,
    EventsSerializer,
    FurnitureSerializer,
    FashionSerializer,
    JobsSerializer,
    ServicesSerializer,
    SportsHobbySerializer,
    KidsSerializer,
)


class VehicleAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = VehicleListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = VehicleListing

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class RealEstateAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = RealEstateListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RealEstateSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class ElectronicsAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = ElectronicsListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ElectronicsSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class EventsAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = EventsListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EventsSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class FashionAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = FashionListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = FashionSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class JobsAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = JobsListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = JobsSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class ServicesAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = ServicesListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ServicesSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class SortsHobbyAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = SportsHobbyListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SportsHobbySerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class KidsAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = KidsListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = KidsSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class FurnitureAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = FurnitureListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = FurnitureSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add vehicle listings.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(data=request.data)
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )
