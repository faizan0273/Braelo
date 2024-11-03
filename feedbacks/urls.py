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
from feedbacks.api.feedbacks import Requests, Feedback

urlpatterns = [
    path('request', Requests.as_view(), name='user-request'),
    path('feedback', Feedback.as_view(), name='user-feedback'),
]
