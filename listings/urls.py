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

from Braelo.listings.api.listing import Listing
from Braelo.listings.api.category import Categories

urlpatterns = [
    path('meta', Categories.as_view(), name='categories-list'),
    path('create', Listing.as_view(), name='create-listing'),
]
