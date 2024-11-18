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

from listings.api.category import Categories
from listings.api.fetch_listings import SavedListing, UserListing, LookupListing
from listings.api.upsert_listing import (
    VehicleAPI,
    RealEstateAPI,
    EventsAPI,
    FashionAPI,
    FurnitureAPI,
    JobsAPI,
    KidsAPI,
    ServicesAPI,
    SportsHobbyAPI,
    ElectronicsAPI,
)
from listings.api.paginate_listing import (
    PaginateVehicle,
    PaginateRealEstate,
    PaginateElectronics,
    PaginateEvents,
    PaginateFashion,
    PaginateJobs,
    PaginateServices,
    PaginateSportsHobby,
    PaginateKids,
    PaginateFurniture,
)
from listings.api.saved_listing import (
    SaveListing,
    FlipListingStatus,
    UnSaveListing,
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
    path('sportshobby', SportsHobbyAPI.as_view(), name='sportshobby-listing'),
    path('electronics', ElectronicsAPI.as_view(), name='electronics-listing'),
    # Pagination's listings
    path(
        'paginate/vehicles',
        PaginateVehicle.as_view(),
        name='paginate-vehicle',
    ),
    path(
        'paginate/realestate',
        PaginateRealEstate.as_view(),
        name='paginate-realestate',
    ),
    path(
        'paginate/electronics',
        PaginateElectronics.as_view(),
        name='paginate-electronics',
    ),
    path(
        'paginate/events',
        PaginateEvents.as_view(),
        name='paginate-events',
    ),
    path(
        'paginate/fashion',
        PaginateFashion.as_view(),
        name='paginate-fashion',
    ),
    path(
        'paginate/jobs',
        PaginateJobs.as_view(),
        name='paginate-jobs',
    ),
    path(
        'paginate/services',
        PaginateServices.as_view(),
        name='paginate-services',
    ),
    path(
        'paginate/sportshobby',
        PaginateSportsHobby.as_view(),
        name='paginate-sportshobby',
    ),
    path(
        'paginate/kids',
        PaginateKids.as_view(),
        name='paginate-kids',
    ),
    path(
        'paginate/furniture',
        PaginateFurniture.as_view(),
        name='paginate-furniture',
    ),
    # Saved items
    path('save', SaveListing.as_view(), name='save-listing'),
    path('get-save', SavedListing.as_view(), name='get-save-lisitngs'),
    path('unsave', UnSaveListing.as_view(), name='unsave-listing'),
    # Searching
    # User own listings & Look up
    path('user/all', UserListing.as_view(), name='user-all-listings'),
    path('lookup', LookupListing.as_view(), name='user-specific-listings'),
    # Flip listing status
    path('flip/status', FlipListingStatus.as_view(), name='flip-status'),
]
