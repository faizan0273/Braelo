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

from .api.listing import Listing
from .api.category import Categories

urlpatterns = [
    path('meta', Categories.as_view(), name='categories-list'),
    path('create', Listing.as_view(), name='create-listing'),
]
