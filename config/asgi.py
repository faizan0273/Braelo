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

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

from config.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from chats import routing

# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(
#             JWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns))
#         ),
#     }
# )

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
# JWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns))
