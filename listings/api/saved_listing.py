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

from django.db import transaction
from django.db.models import F
from users.models import User
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics


from listings.api import MODEL_MAP
from listings.models import SavedItem
from helpers.models import ListSync
from listings.api.upsert_listing import Listing
from listings.serializers import SavedItemSerializer
from helpers import handle_exceptions, response, ListSynchronize


class SaveListing(Listing):
    '''
    Save user listed listing.
    '''

    queryset = SavedItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedItemSerializer


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


class FlipListingStatus(generics.CreateAPIView):
    '''
    Flip listing status.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        req = request.data
        user_id = request.user.id
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
        listing_limit = User.objects.filter(id=user_id).first()
        if not listing_limit.is_business and listing_status:
            if listing_limit.allowed_listings == 10:
                raise ValidationError(
                    {'Listing Limit': 'Cannot Exceed 10 For Normal User'}
                )

        model = MODEL_MAP[category]
        ListSynchronize.flip_status(
            listing_id=listing_id,
            status=listing_status,
            model=model,
            user_id=user_id,
        )
        ListSynchronize.flip_status(
            listing_id=listing_id, status=listing_status, user_id=user_id
        )
        # Only updates if user is Normal User
        if not listing_limit.is_business:
            listing_limit.allowed_listings += 1 if listing_status else -1
            listing_limit.save()

        return response(
            status=status.HTTP_200_OK,
            message='Flipped listing status successfully',
            data={},
        )


class DeleteListing(generics.RetrieveDestroyAPIView):
    '''
    deletes a listing from category and listsync collection
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def delete(self, request):
        user_id = request.user.id
        listing_id = request.data.get('listing_id')
        category = request.data.get('category')
        if not category or not listing_id:
            raise ValidationError(
                {
                    'Parameters': 'Category and listing_id are required parameters.'
                }
            )
        if category not in MODEL_MAP:
            raise ValidationError(
                {
                    'category': f'Invalid category. Choose from {list(MODEL_MAP.keys())}.'
                }
            )
        with transaction.atomic():
            deleted_category_count = (
                MODEL_MAP[category]
                .objects.filter(user_id=user_id, id=listing_id)
                .delete()
            )
            if deleted_category_count == 0:
                return response(
                    status=status.HTTP_204_NO_CONTENT,
                    message='No listing Found in category collection',
                    data={},
                )

            deleted_listsync_count = ListSync.objects.filter(
                user_id=user_id, listing_id=listing_id
            ).delete()
            if deleted_listsync_count == 0:
                return response(
                    status=status.HTTP_204_NO_CONTENT,
                    message='No listing Found in listsync collection',
                    data={},
                )
            User.objects.filter(id=user_id, is_business=False).update(
                allowed_listings=F('allowed_listings') + 1
            )

        return response(
            status=status.HTTP_200_OK,
            message='listing delete successfully',
            data={},
        )
