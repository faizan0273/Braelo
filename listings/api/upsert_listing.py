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

import json
from rest_framework import status
from rest_framework_mongoengine import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from helpers.notifications import LISTINGS_EVENT_DATA
from notifications.serializers.events import EventNotificationSerializer


from listings.models import (
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
    RealEstateListing,
    VehicleListing,
)
from helpers import response, handle_exceptions
from listings.serializers import (
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
)


class Listing(generics.CreateAPIView):
    '''
    Base API endpoint to create a new listing for different categories.
    '''

    permission_classes = [IsAuthenticated]

    def send_notification(self, serializer):
        try:
            listing_id = serializer.data['id']
            category = serializer.data['category']
            user_id = serializer.data['user_id']
            LISTINGS_EVENT_DATA['data']['listing_id'] = listing_id
            LISTINGS_EVENT_DATA['data']['category'] = category
            LISTINGS_EVENT_DATA['data']['user_id'] = user_id
            LISTINGS_EVENT_DATA['user_id'] = [user_id]
            event_serializer = EventNotificationSerializer(
                data=LISTINGS_EVENT_DATA
            )
            event_serializer.is_valid(raise_exception=True)
            event_serializer.save()
        except Exception:
            pass

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add a listing.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        try:
            listing_coordinates = request.data.get('listing_coordinates')
            if not listing_coordinates:
                raise ValidationError(
                    {'listing_coordinates': 'field is required'}
                )
            listing_coordinates = json.loads(listing_coordinates)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                'Invalid JSON format for business_coordinates.'
            ) from exc
        mutable_data = request.data.copy()
        mutable_data['listing_coordinates'] = listing_coordinates
        serializer = self.get_serializer(
            data=mutable_data, context={'request': request}
        )
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_notification(serializer)

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
