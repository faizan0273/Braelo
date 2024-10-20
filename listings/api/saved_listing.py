'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User saved listings endpoints.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from listings.api.listing import Listing
from listings.helpers import handle_exceptions, response
from listings.models import SavedItem, ListSync
from listings.serializers import SavedItemSerializer, ListsyncSerializer


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


class SaveItemAPI(Listing):

    queryset = SavedItem.objects.all()
    serializer_class = SavedItemSerializer


class RetrieveSavedListing(generics.ListAPIView):

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

        return response(
            status=status.HTTP_200_OK,
            message='Saved items retrieved successfully',
            data=serializer.data,
        )


class UserListing(generics.CreateAPIView):
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

        return response(
            status=status.HTTP_200_OK,
            message='Saved items retrieved successfully',
            data=serializer.data,
        )


# todo un save, active, inactive
