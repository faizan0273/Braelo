'''
---------------------------------------------------
Project:        Braelo
Date:           Dec 20, 2024
Author:         Faizan
---------------------------------------------------

Description:
Fetch Business Dashboard endpoints.
---------------------------------------------------
'''


from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated


from helpers import handle_exceptions, response


class BusinessDashboard(generics.CreateAPIView):
    '''
    API endpoint to get business dashboard info based on user_id
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        '''
        GET method to fetch business dashboard.
        :return: business dashboard data.(json)
        '''
        user = request.user
        if not user.is_business:
            raise ValidationError({'User': 'Only Business Users Can Acesss'})
        business_insights = {
            'Clicks': user.listings_clicks,
            'Interactions': user.business_interactions,
            'Listing': user.listings_count,
            'Featured': user.business_featured,
        }
        return response(
            status=status.HTTP_200_OK,
            message='Dashboard Fetched Successfully',
            data=business_insights,
        )
