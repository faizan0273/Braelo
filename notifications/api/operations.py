'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notifications operations endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics

from helpers import handle_exceptions, response
from notifications.serializers.operations import (
    MarkReadSerializer,
    DeleteNotificationSerializer,
)


class MarkNotificationsAsReadAPI(generics.UpdateAPIView):
    '''
    API endpoint to mark one or multiple notifications as read.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = MarkReadSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to mark notifications as read.
        :param request: request object. (dict)
        :return: update status. (json)
        '''
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_count = serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message=f'{updated_count} notification(s) marked as read.',
        )


class DeleteNotificationsAPI(generics.DestroyAPIView):
    '''
    API endpoint to delete specific notifications.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = DeleteNotificationSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to delete notifications.
        :param request: request object. (dict)
        :return: delete status. (json)
        '''
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        deleted_count = serializer.save()
        return response(
            status=status.HTTP_200_OK,
            message=f'{deleted_count} notification(s) deleted successfully.',
        )
