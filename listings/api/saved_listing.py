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

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics

from listings.api import MODEL_MAP
from listings.api.upsert_listing import Listing
from listings.helpers import handle_exceptions, response
from listings.helpers.listsync import ListSynchronize
from listings.models import SavedItem
from listings.serializers import SavedItemSerializer


class SaveListing(Listing):
    '''
    Save user listed listing.
    '''

    queryset = SavedItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedItemSerializer


class FlipListingStatus(generics.CreateAPIView):
    '''
    Flip listing status.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        req = request.data
        listing_status = req.get('status')
        category = req.get('category')
        listing_id = req.get('listing_id')
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
        model = MODEL_MAP[category]
        ListSynchronize.flip_status(
            listing_id=listing_id, status=listing_status, model=model
        )
        ListSynchronize.flip_status(
            listing_id=listing_id, status=listing_status
        )
        return response(
            status=status.HTTP_200_OK,
            message='Flipped listing status successfully',
            data={},
        )


class UnSaveListing(generics.RetrieveDestroyAPIView):
    '''
    Delete a listing from the saved listing collection.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def delete(self, request):
        req = request.data
        listing_id = req.get('listing_id')
        if not listing_id:
            raise ValidationError('listing_id is required.')
        deleted_count, _ = SavedItem.objects.filter(
            listing_id=listing_id
        ).delete()
        if deleted_count == 0:
            return response(
                status=status.HTTP_204_NO_CONTENT,
                message='No listing Found',
                data={},
            )

        return response(
            status=status.HTTP_200_OK,
            message='Deleted Listing successfully',
            data={},
        )
