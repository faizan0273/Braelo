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
from listings.api.fetch_listings import (
    SavedListing,
    UserListing,
    LookupListing,
    Recommendations,
    Recent,
)
from listings.api.update_listing import (
    RealEstateUpdateAPI,
    VehicleUpdateAPI,
    ElectronicsUpdateAPI,
    EventsUpdateAPI,
    FashionUpdateAPI,
    JobsUpdateAPI,
    ServicesUpdateAPI,
    SportsHobbyUpdateAPI,
    KidsUpdateAPI,
    FurnitureUpdateAPI,
)
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
    DeleteListing,
)
from listings.api.search import (
    Search,
    RecentSearches,
    DeleteSearches,
)

urlpatterns = [
    path('jobs', JobsAPI.as_view()),
    path('kids', KidsAPI.as_view()),
    path('meta', Categories.as_view()),
    path('events', EventsAPI.as_view()),
    path('vehicle', VehicleAPI.as_view()),
    path('fashion', FashionAPI.as_view()),
    path('services', ServicesAPI.as_view()),
    path('furniture', FurnitureAPI.as_view()),
    path('realestate', RealEstateAPI.as_view()),
    path('sportshobby', SportsHobbyAPI.as_view()),
    path('electronics', ElectronicsAPI.as_view()),
    # Update api
    path('jobs/<str:pk>', JobsUpdateAPI.as_view()),
    path('kids/<str:pk>', KidsUpdateAPI.as_view()),
    path('events/<str:pk>', EventsUpdateAPI.as_view()),
    path('fashion/<str:pk>', FashionUpdateAPI.as_view()),
    path('vehicles/<str:pk>', VehicleUpdateAPI.as_view()),
    path('services/<str:pk>', ServicesUpdateAPI.as_view()),
    path('furniture/<str:pk>', FurnitureUpdateAPI.as_view()),
    path('realestate/<str:pk>', RealEstateUpdateAPI.as_view()),
    path('electronics/<str:pk>', ElectronicsUpdateAPI.as_view()),
    path('sportshobby/<str:pk>', SportsHobbyUpdateAPI.as_view()),
    # Pagination's listings
    path('paginate/jobs', PaginateJobs.as_view()),
    path('paginate/kids', PaginateKids.as_view()),
    path('paginate/events', PaginateEvents.as_view()),
    path('paginate/fashion', PaginateFashion.as_view()),
    path('paginate/vehicles', PaginateVehicle.as_view()),
    path('paginate/services', PaginateServices.as_view()),
    path('paginate/furniture', PaginateFurniture.as_view()),
    path('paginate/realestate', PaginateRealEstate.as_view()),
    path('paginate/electronics', PaginateElectronics.as_view()),
    path('paginate/sportshobby', PaginateSportsHobby.as_view()),
    # Saved items
    path('save', SaveListing.as_view()),
    path('get-save', SavedListing.as_view()),
    path('unsave', UnSaveListing.as_view()),
    # Searching
    # User own listings & Look up
    path('user/all', UserListing.as_view()),
    path('lookup', LookupListing.as_view()),
    # Flip listing status
    path('flip/status', FlipListingStatus.as_view()),
    # delete listing
    path('delete', DeleteListing.as_view()),
    # Recommendations
    path('recommendations', Recommendations.as_view()),
    # Recent
    path('recent', Recent.as_view()),
    # Search
    path('search', Search.as_view()),
    # Recent Searches
    path('recent/searches', RecentSearches.as_view()),
    # Delete Recent Searches
    path('delete/searches', DeleteSearches.as_view()),
]
