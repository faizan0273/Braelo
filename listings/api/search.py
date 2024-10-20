'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Search of Listings endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics
from rest_framework.exceptions import ValidationError

from listings.helpers import handle_exceptions, response
from listings.models import (
    RealEstateListing,
    ServicesListing,
    EventsListing,
    JobsListing,
    ElectronicsListing,
    FurnitureListing,
    FashionListing,
    KidsListing,
    SportsHobbyListing,
    VehicleListing,
)

# from listings.serializers import LookupListingSerializer


class LookupListing(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    MODEL_MAP = {
        'vehicles': VehicleListing,
        'real estate': RealEstateListing,
        'services': ServicesListing,
        'events': EventsListing,
        'jobs': JobsListing,
        'electronics': ElectronicsListing,
        'furniture': FurnitureListing,
        'fashion': FashionListing,
        'kids': KidsListing,
        'sports & hobby': SportsHobbyListing,
    }

    @handle_exceptions
    def get(self, request, **kwargs):
        '''
        Get method to fetch listing by id.
        :param request: request object. (dict)
        :return: Listing object. (dict)
        '''
        user = request.user
        user_id = user.id
        category = request.data.get('category')
        listing_id = request.data.get('listing_id')
        if not category or not listing_id:
            raise ValidationError(
                'Category and listing_id are required parameters.'
            )

        # Validate category
        if category not in self.MODEL_MAP:
            raise ValidationError(
                {
                    'category': f'Invalid category. Choose from {list(self.MODEL_MAP.keys())}.'
                }
            )

        # Fetch the corresponding model
        model = self.MODEL_MAP[category]

        listing = model.objects.get(id=listing_id, user_id=user_id)

        listing_data = listing.to_mongo().to_dict()  # Convert to dict
        listing_data.pop('_id', None)
        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=listing_data,
        )
