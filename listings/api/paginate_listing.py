'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Pagination of Listing endpoints.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from helpers import response

from helpers import CATEGORIES
from listings.models import (
    VehicleListing,
    RealEstateListing,
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
)
from listings.serializers import (
    VehicleSerializer,
    RealEstateSerializer,
    ElectronicsSerializer,
    FashionSerializer,
    JobsSerializer,
    ServicesSerializer,
    SportsHobbySerializer,
    KidsSerializer,
    FurnitureSerializer,
    EventsSerializer,
)


class Pagination(PageNumberPagination):
    '''
    Listing pagination configurations.
    '''

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        '''
        Overriding a function to convert a list into a dict
        '''
        dict_of_dicts = {item['id']: item for item in data}
        pagination_data = {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': dict_of_dicts,
        }
        return response(
            status=status.HTTP_200_OK,
            message='listings fetched successfully',
            data=pagination_data,
        )


class PaginateVehicle(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest vehicle listings with pagination.
    '''

    queryset = VehicleListing.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = Pagination
    serializer_class = VehicleSerializer


class PaginateRealEstate(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest real estate listings with pagination.
    '''

    queryset = RealEstateListing.objects.all()
    pagination_class = Pagination
    serializer_class = RealEstateSerializer


class PaginateElectronics(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest electronics listings with pagination.
    '''

    queryset = ElectronicsListing.objects.all()
    pagination_class = Pagination
    serializer_class = ElectronicsSerializer


class PaginateEvents(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest events listings with pagination.
    '''

    queryset = EventsListing.objects.all()
    pagination_class = Pagination
    serializer_class = EventsSerializer


class PaginateFashion(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest fashion listings with pagination.
    '''

    queryset = FashionListing.objects.all()
    pagination_class = Pagination
    serializer_class = FashionSerializer


class PaginateJobs(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest jobs listings with pagination.
    '''

    queryset = JobsListing.objects.all()
    pagination_class = Pagination
    serializer_class = JobsSerializer


class PaginateServices(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest services listings with pagination.
    '''

    queryset = ServicesListing.objects.all()
    pagination_class = Pagination
    serializer_class = ServicesSerializer


class PaginateSportsHobby(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest sports and hobby listings with pagination.
    '''

    queryset = SportsHobbyListing.objects.all()
    pagination_class = Pagination
    serializer_class = SportsHobbySerializer


class PaginateKids(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest kids listings with pagination.
    '''

    queryset = KidsListing.objects.all()
    pagination_class = Pagination
    serializer_class = KidsSerializer


class PaginateFurniture(generics.ListAPIView):
    '''
    Endpoint to retrieve the latest furniture listings with pagination.
    '''

    queryset = FurnitureListing.objects.all()
    pagination_class = Pagination
    serializer_class = FurnitureSerializer
