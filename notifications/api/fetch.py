'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
get notifications endpoints.
---------------------------------------------------
'''

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_mongoengine import generics

from notifications.models import Notification
from notifications.serializers.fetch import NotificationSerializer


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class FetchNotificationsAPI(generics.ListAPIView):
    '''
    API endpoint to fetch all notifications for the authenticated user.
    '''

    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user_id=user.id)
