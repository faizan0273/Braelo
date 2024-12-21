'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
notifications endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics

from helpers import handle_exceptions, response
from notifications.serializers.admin import AdminNotificationSerializer


class AdminNotificationAPI(generics.CreateAPIView):
    '''
    API endpoint for admins to send notifications to specific users or broadcast.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = AdminNotificationSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to send admin notifications.
        :param request: request object. (dict)
        :return: notification status. (json)
        '''
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Admin notification sent successfully.',
            data=serializer.data,
        )
