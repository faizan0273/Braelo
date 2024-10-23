"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User saved listings endpoints.
---------------------------------------------------
"""

from django.http import JsonResponse
from rest_framework import status
from rest_framework import generics as drf_generics
from rest_framework.exceptions import ValidationError
from rest_framework_mongoengine import generics
from rest_framework.permissions import IsAuthenticated

from listings.api import MODEL_MAP
from listings.models import SavedItem
from listings.api.upsert_listing import Listing
from listings.serializers import SavedItemSerializer,UnsaveItemSerializer
from listings.helpers.listsync import ListSynchronize
from listings.helpers import handle_exceptions, response


class SaveListing(Listing):
    '''
    Save user listed listing.
    '''

    queryset = SavedItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedItemSerializer


# todo un save


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
            message="Flipped listing status successfully",
            data={},
        )


class UnsaveUserListing(drf_generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UnsaveItemSerializer

    @handle_exceptions
    def delete(self, request):
          
            serializer = UnsaveItemSerializer(data=request.data)
            if serializer.is_valid():
                listing_id = serializer.validated_data['listing_id']
                listing_unsaved = SavedItem.objects.filter(listing_id=listing_id).delete()
                if listing_unsaved == 0:
                    return JsonResponse(
                        {   "status":status.HTTP_204_NO_CONTENT,
                            "message": "no listing to delete"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

                return JsonResponse(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Saved item deleted successfully",
                },
                status=status.HTTP_200_OK,
                )
            
            else:
             return JsonResponse(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                )
