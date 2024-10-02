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

from ..models.real_estate import RealEstateListing
from ..models.vehicle import VehicleListing
from ..helpers import response, handle_exceptions
from ..serializers import (
    ListingSerializer,
    VehicleListingSerializer,
    RealEstateListingSerializer,
)


class Listing(generics.CreateAPIView):
    '''
    API endpoint to create a new listing.
    '''

    permission_classes = [AllowAny]
    serializer_class = ListingSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add listings.
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


class VehicleListingAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = VehicleListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = VehicleListingSerializer

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


class RealEstateListingAPI(generics.CreateAPIView):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = RealEstateListing.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RealEstateListingSerializer

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
