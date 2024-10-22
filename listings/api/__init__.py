'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
__init__.py file for endpoints imports.
---------------------------------------------------
'''

from listings.api.category import *
from listings.models import (
    VehicleListing,
    RealEstateListing,
    ServicesListing,
    EventsListing,
    JobsListing,
    ElectronicsListing,
    FurnitureListing,
    FashionListing,
    KidsListing,
    SportsHobbyListing,
)

MODEL_MAP = {
    'vehicles': VehicleListing,
    'real estate': RealEstateListing,
    'services': ServicesListing,
    'events': EventsListing,
    'jobs': JobsListing,
    'electronics': ElectronicsListing,
    'furniture': FurnitureListing,
    'fashion': FashionListing,
    'kids': KidsListing,
    'sports & hobby': SportsHobbyListing,
}
