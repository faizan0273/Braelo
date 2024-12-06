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

from bson import ObjectId
from rest_framework import status
from mongoengine.errors import DoesNotExist
from rest_framework_mongoengine import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from listings.models import (
    RealEstateListing,
    VehicleListing,
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
)
from helpers import response, handle_exceptions
from listings.serializers import (
    RealEstateUpdateSerializer,
    VehicleUpdateSerializer,
    ElectronicsUpdateSerializer,
    EventsUpdateSerializer,
    FashionUpdateSerializer,
    JobsUpdateSerializer,
    ServicesUpdateSerializer,
    SportsHobbyUpdateSerializer,
    KidsUpdateSerializer,
    FurnitureUpdateSerializer,
)


class UpdateListing(generics.UpdateAPIView):
    '''
    Base API endpoint to update a listing.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def put(self, request, *args, **kwargs):
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
            context={'request': request, 'is_update': True},
        )
        # Validate and update the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message='Listing updated successfully',
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
            return self.queryset.get(id=ObjectId(pk))
        except DoesNotExist:
            raise ValidationError({'detail': 'Listing not found.'})


class VehicleUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = VehicleListing.objects.all()
    serializer_class = VehicleUpdateSerializer


class RealEstateUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = RealEstateListing.objects.all()
    serializer_class = RealEstateUpdateSerializer


class ElectronicsUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = ElectronicsListing.objects.all()
    serializer_class = ElectronicsUpdateSerializer


class EventsUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = EventsListing.objects.all()
    serializer_class = EventsUpdateSerializer


class FashionUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = FashionListing.objects.all()
    serializer_class = FashionUpdateSerializer


class JobsUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = JobsListing.objects.all()
    serializer_class = JobsUpdateSerializer


class ServicesUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = ServicesListing.objects.all()
    serializer_class = ServicesUpdateSerializer


class SportsHobbyUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = SportsHobbyListing.objects.all()
    serializer_class = SportsHobbyUpdateSerializer


class KidsUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = KidsListing.objects.all()
    serializer_class = KidsUpdateSerializer


class FurnitureUpdateAPI(UpdateListing):
    '''
    API endpoint to update a new vehicle listings.
    '''

    queryset = FurnitureListing.objects.all()
    serializer_class = FurnitureUpdateSerializer
