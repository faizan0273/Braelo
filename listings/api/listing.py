'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Populate Listing and save listings endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework_mongoengine import generics
from rest_framework.permissions import IsAuthenticated

from ..models import (
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
    SavedItem,
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
    VehicleSerializer,
    SavedItemSerializer,
)


class Listing(generics.CreateAPIView):
    '''
    Base API endpoint to create a new listing for different categories.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add a listing.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class VehicleAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = VehicleListing.objects.all()
    serializer_class = VehicleSerializer


class RealEstateAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = RealEstateListing.objects.all()
    serializer_class = RealEstateSerializer


class ElectronicsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = ElectronicsListing.objects.all()
    serializer_class = ElectronicsSerializer


class EventsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = EventsListing.objects.all()
    serializer_class = EventsSerializer


class FashionAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = FashionListing.objects.all()
    serializer_class = FashionSerializer


class JobsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = JobsListing.objects.all()
    serializer_class = JobsSerializer


class ServicesAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = ServicesListing.objects.all()
    serializer_class = ServicesSerializer


class SportsHobbyAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = SportsHobbyListing.objects.all()
    serializer_class = SportsHobbySerializer


class KidsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = KidsListing.objects.all()
    serializer_class = KidsSerializer


class FurnitureAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    queryset = FurnitureListing.objects.all()
    serializer_class = FurnitureSerializer


class SaveItemAPI(Listing):

    queryset = SavedItem.objects.all()
    serializer_class = SavedItemSerializer
