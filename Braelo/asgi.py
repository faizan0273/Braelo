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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Braelo.settings')

application = get_asgi_application()
