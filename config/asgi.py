'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
ASGI config for Braelo project.
It exposes the ASGI callable as a module-level variable named ``application``.
---------------------------------------------------
'''

import os

from chats import routing
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns,
            )
        ),
    }
)
