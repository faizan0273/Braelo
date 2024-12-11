'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Fetch User listings endpoints.
---------------------------------------------------
'''

from mongoengine import Q
from mongoengine.errors import DoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from helpers import ListSync
from listings.api import MODEL_MAP
from listings.api.paginate_listing import Pagination
from listings.models import SavedItem
from helpers import handle_exceptions, response
from users.models import Interest
from rest_framework.exceptions import ValidationError
from listings.serializers import (
    SavedItemSerializer,
    ListsyncSerializer,
)


def get_user_listings(collection, user_id, offset, limit):
    '''
    Retrieves listings from given collection.
    :param collection: CMongo db collection name. (Dict)
    :param user_id: user id. (int)
    :param offset: records to skip. (int)
    :param limit: records to fetch from db. (int)
    :return:
    '''
    sort = '-created_at'
    queryset = (
        collection.objects.filter(user_id=user_id)
        .order_by(sort)
        .skip(offset)
        .limit(limit)
    )
    return list(queryset)


def get_user_recommendations(user_id):
    '''
    Retrieves user interests.
    :param user_id: user id information. (int)
    :return: users interests. (list)
    '''
    try:
        interest = Interest.objects.get(user_id=user_id)
        return interest.tags
    except Interest.DoesNotExist:
        return []


class SavedListing(generics.ListAPIView):
    '''
    Fetch User Saved listing.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        '''
        GET method to retrieve saved items for the user.
        :param request: request object. (dict)
        :return: saved items. (json)
        '''
        user_id = request.user.id

        # Fetch all listings for the user across all categories
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        listings = get_user_listings(SavedItem, user_id, offset, limit)
        serializer = SavedItemSerializer(listings, many=True)
        saved_listings = {item['id']: item for item in serializer.data}

        return response(
            status=status.HTTP_200_OK,
            message='Saved items retrieved successfully',
            data=saved_listings,
        )


class UserListing(generics.CreateAPIView):
    '''
    Fetch User listed listing.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        # Get the logged-in user's ID
        user_id = request.user.id

        # Fetch all listings for the user across all categories
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        listings = get_user_listings(ListSync, user_id, offset, limit)
        serializer = ListsyncSerializer(listings, many=True)
        user_listings = {item['id']: item for item in serializer.data}

        return response(
            status=status.HTTP_200_OK,
            message='Saved items retrieved successfully',
            data=user_listings,
        )


class LookupListing(generics.CreateAPIView):
    '''
    look up user listing based on id.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request, **kwargs):
        '''
        Get method to fetch listing by id.
        :param request: request object. (dict)
        :return: Listing object. (dict)
        '''
        try:
            user = request.user
            user_id = user.id
            category = request.data.get('category')
            listing_id = request.data.get('listing_id')
            if not category or not listing_id:
                raise ValidationError(
                    'Category and listing_id are required parameters.'
                )

            # Validate category
            if category not in MODEL_MAP:
                raise ValidationError(
                    {
                        'category': f'Invalid category. Choose from {list(MODEL_MAP.keys())}.'
                    }
                )

            # Fetch the corresponding model
            model = MODEL_MAP[category]

            listing = model.objects.get(id=listing_id, user_id=user_id)
            listing_data = listing.to_mongo().to_dict()  # Convert to dict
            listing_data.pop('_id', None)
            if user.is_business:
                user.listings_clicks += 1
                user.save()
            return response(
                status=status.HTTP_200_OK,
                message='Listing fetched successfully',
                data=listing_data,
            )
        except DoesNotExist:
            raise ValidationError({'Listings': 'No listings found'})


class Recent(generics.ListAPIView):

    pagination_class = Pagination
    queryset = ListSync.objects.all()
    serializer_class = ListsyncSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class Recommendations(generics.ListAPIView):
    '''
    Fetch listings based on user recommendation.
    '''

    pagination_class = Pagination
    serializer_class = ListsyncSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.request.user.id
        interests = get_user_recommendations(user_id)
        try:
            if not interests:
                return ListSync.objects.all()
            queryset = ListSync.objects.filter(
                Q(category__in=interests) | Q(subcategory__in=interests)
            )
        except Exception as exc:
            raise ValidationError({'Listsync': str(exc)})
        return queryset
