'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
routing file.
---------------------------------------------------
'''

from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("chat_id/<chat_id>", ChatroomConsumer.as_asgi()),
]
