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
from helpers.notifications import SAVED_EVENT_DATA
from listings.api.upsert_listing import Listing
from listings.serializers import SavedItemSerializer
from helpers.constants import USER_LISTINGS_THRESHOLD
from helpers import handle_exceptions, response, ListSynchronize

from notifications.serializers.events import EventNotificationSerializer


class SaveListing(generics.CreateAPIView):
    '''
    Save user listed listing.
    '''

    queryset = SavedItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedItemSerializer

    def create(self, request, *args, **kwargs):
        save_param = request.GET.get('save')

        if save_param is None or save_param not in ['True', 'False']:
            raise ValidationError(
                {'Correct Param Required': '"save" should be True or False'}
            )

        if save_param == 'True':
            serializer = self.get_serializer(
                data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            SAVED_EVENT_DATA['data']['listing_id'] = request.data.get(
                'listing_id'
            )
            SAVED_EVENT_DATA['user_id'] = [request.user.id]
            try:
                event_serializer = EventNotificationSerializer(
                    data=SAVED_EVENT_DATA
                )
                event_serializer.is_valid(raise_exception=True)
                event_serializer.save()
            except Exception:
                pass

            return response(
                status=status.HTTP_201_CREATED,
                message='Listings Saved Successfully',
                data=serializer.data,
            )
        # Unsave functionality if PARAM is False
        req = request.data
        listing_id = req.get('listing_id')
        if not listing_id:
            raise ValidationError('listing_id is required.')
        deleted_count = SavedItem.objects.filter(listing_id=listing_id).delete()
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
            if listing_limit.listings_count == USER_LISTINGS_THRESHOLD:
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
        #  updates the listings count for business & user
        if listing_status:
            listing_limit.listings_count += 1
        elif not listing_limit.is_business and listing_limit.listings_count > 0:
            listing_limit.listings_count -= 1
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
                listings_count=F('listings_count') - 1
            )

        return response(
            status=status.HTTP_200_OK,
            message='listing delete successfully',
            data={},
        )
