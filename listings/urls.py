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
from .api.listing import (
    VehicleAPI,
    RealEstateAPI,
    EventsAPI,
    FashionAPI,
    FurnitureAPI,
    JobsAPI,
    KidsAPI,
    ServicesAPI,
    SortsHobbyAPI,
    ElectronicsAPI,
)

urlpatterns = [
    path('jobs', JobsAPI.as_view(), name='jobs-listing'),
    path('kids', KidsAPI.as_view(), name='kids-listing'),
    path('meta', Categories.as_view(), name='categories-list'),
    path('events', EventsAPI.as_view(), name='events-listing'),
    path('vehicle', VehicleAPI.as_view(), name='vehicle-listing'),
    path('fashion', FashionAPI.as_view(), name='fashion-listing'),
    path('services', ServicesAPI.as_view(), name='services-listing'),
    path('furniture', FurnitureAPI.as_view(), name='furniture-listing'),
    path('realestate', RealEstateAPI.as_view(), name='realestate-listing'),
    path('sportshobby', SortsHobbyAPI.as_view(), name='sportshobby-listing'),
    path('electronics', ElectronicsAPI.as_view(), name='electronics-listing'),
]
