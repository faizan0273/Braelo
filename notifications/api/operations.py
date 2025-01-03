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
from notifications.models import Notification
from rest_framework import generics
from rest_framework.exceptions import ValidationError


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

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to mark notifications as read.
        :param request: request object. (dict)
        :return: update status. (json)
        '''
        notification_id = request.data.get('notification_id')
        if not notification_id:
            raise ValidationError(
                {'Notification': 'notfication_id is required'}
            )
        notification = Notification.objects(id=notification_id).first()
        if not notification:
            return response(
                status=status.HTTP_404_NOT_FOUND,
                message='Notification not found',
                data={},
            )
        if not notification.is_read:
            notification.is_read = True
            notification.sent = True
            notification.save()
        return response(
            status=status.HTTP_200_OK,
            message='Notification read successfully',
            data={},
        )


class DeleteNotificationsAPI(generics.DestroyAPIView):
    '''
    API endpoint to delete specific notifications.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to delete notifications.
        :param request: request object. (dict)
        :return: delete status. (json)
        '''
        user_id = str(request.user.id)
        notification_id = request.data.get('notification_id')
        if not notification_id:
            raise ValidationError({'ID': 'notification id required'})
        delete_notification = Notification.objects.filter(
            id=notification_id, user_id=user_id
        ).first()
        if not delete_notification:
            return response(
                status=status.HTTP_204_NO_CONTENT,
                message='No notification found',
                data={},
            )
        delete_notification.delete()
        delete_notification.save()
        return response(
            status=status.HTTP_204_NO_CONTENT,
            message=' notification deleted successfully',
            data={},
        )
