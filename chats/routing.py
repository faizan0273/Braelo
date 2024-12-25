from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("chat_id/<chat_id>", ChatroomConsumer.as_asgi()),
]
