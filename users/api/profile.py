'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Haseeb
---------------------------------------------------

Description:
Update profile api.
---------------------------------------------------
'''

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from users.models import User
from users.serializers import (
    UpdateProfileSerializer,
    UserProfileSerializer,
    DeactivateUserSerializer,
)
from helpers import handle_exceptions, response, ListSync
from users.models.business import Business


class UpdateProfile(generics.CreateAPIView):
    '''
    Update name fields endpoint.
    '''

    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        Handle the Profile Update mechanism.
        '''
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_data = serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message='Profile updated successfully',
            data=updated_data,
        )


class UserProfile(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return response(
            status=status.HTTP_200_OK,
            message='Profile retrieved successfully',
            data=serializer.data,  # Send serialized user data
        )


class AboutUser(generics.CreateAPIView):
    '''
    Retrieve and Display User Information.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        user = request.user
        created_at = user.created_at
        created_at = created_at.strftime('%B %Y')

        user_data = {
            'Name': user.name,
            'Created_at': created_at,
        }
        return response(
            status=status.HTTP_200_OK,
            message='User information fetched successfully',
            data=user_data,
        )


class PublicProfile(generics.CreateAPIView):
    '''
    Get Public profile.
    '''

    permission_classes = [AllowAny]

    @handle_exceptions
    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            # Get user_id from the request data
            user_id = request.data.get('user_id')
        if not user_id:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='user_id is required',
                data={},
            )
        user = get_object_or_404(User, id=user_id)
        member_since = user.created_at.strftime('%b %Y')

        # Count the listings in ListSync associated with the user_id
        listing_count = ListSync.objects.filter(user_id=user_id).count()

        # Prepare the response data
        profile_data = {
            'listing_count': listing_count,
            'name': user.name,
            'member_since': member_since,
        }
        return response(
            status=status.HTTP_200_OK,
            message='User information fetched successfully',
            data=profile_data,
        )


class DeactivateUser(generics.CreateAPIView):

    serializer_class = DeactivateUserSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        Handle the Profile inactive mechanism.
        '''
        context = {'request': request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        updated_data = serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message='Profile deleted successfully',
            data=updated_data,
        )


class FlipUserStatus(generics.CreateAPIView):
    '''
    Flips normal user into business user
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request):
        user = request.user
        user_id = user.id
        user_status = request.data.get('status')

        # Validate user_status
        if user_status not in ['user', 'business']:
            raise ValidationError(
                {'Status': 'Status must be either "user" or "business".'}
            )

        # Handle 'business' status cases
        if user_status == 'business':
            if user.previous_business and Business.objects(
                user_id=user_id, is_active=True
            ):
                user.is_business = True
                user.save()
                return response(
                    status=status.HTTP_200_OK,
                    message='Business Already Exists for User',
                    data={},
                )
            if Business.objects(user_id=user_id, is_active=False).first():
                return response(
                    status=status.HTTP_200_OK,
                    message='Business Already Exists for User. Business is Deactivated, Please Activate.',
                    data={},
                )
            if user.is_business:
                raise ValidationError(
                    {'User': 'User is already a Business User'}
                )

        # Handle 'user' status cases
        if user_status == 'user' and not user.is_business:
            raise ValidationError({'User': 'User is already a Normal User'})

        # Flip user status
        user.is_business = user_status == 'business'
        user.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Flipped User Status Successfully',
            data={},
        )
