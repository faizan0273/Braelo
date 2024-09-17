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
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from Braeloo.listings.models import Category
from Braeloo.users.helpers import response


class Categories(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        '''
        GET method to return categories.
        :return: categories and sub-categories. (json)
        '''

        records = Category.objects.all()
        categories = {}
        # Categories
        for category in records:
            categories[category.name] = {
                'id': str(category['id']),
                'subcategories': [],
            }
            # subcategories
            for subcategory in category['subcategories']:
                categories[category.name]['subcategories'].append(
                    {
                        'id': str(subcategory.id),
                        'name': subcategory.name,
                    }
                )
        return response(
            status=status.HTTP_200_OK,
            message='Categories Meta',
            data=categories,
        )
