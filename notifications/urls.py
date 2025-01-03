'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
End points registry file.
---------------------------------------------------
'''

from django.urls import path
from notifications.api.events import EventNotificationAPI
from notifications.api.fetch import FetchNotificationsAPI
from notifications.api.operations import (
    MarkNotificationsAsReadAPI,
    DeleteNotificationsAPI,
)

urlpatterns = [
    # Fetch notifications
    path('paginate', FetchNotificationsAPI.as_view()),
    # Admin broadcast
    path('send', EventNotificationAPI.as_view()),
    # mark read
    path('read', MarkNotificationsAsReadAPI.as_view()),
    # delete notification
    path('delete', DeleteNotificationsAPI.as_view()),
]
