'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing categories endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_mongoengine import generics

from helpers import response, CATEGORIES


class Categories(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        '''
        GET method to return categories.
        :return: categories and sub-categories. (json)
        '''

        return response(
            status=status.HTTP_200_OK,
            message='Categories Meta',
            data=CATEGORIES,
        )
