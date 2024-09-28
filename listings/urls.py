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

from .api.category import Categories
from .api.listing import Listing, VehicleListingAPI

urlpatterns = [
    path('meta', Categories.as_view(), name='categories-list'),
    path('create', Listing.as_view(), name='create-listing'),
    path('vehicle', VehicleListingAPI.as_view(), name='vehicle-listing'),
]
