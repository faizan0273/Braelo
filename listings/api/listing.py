'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from ..serializers import ListingSerializer
from ..helpers import response


class Listing(APIView):
    """
    API endpoint to create a new listing.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ListingSerializer(data=request.data)

        # Validate and create the listing if valid
        if serializer.is_valid():
            serializer.save()
            return response(
                status=status.HTTP_201_CREATED,
                message='Listing created successfully',
                data=serializer.data,
            )
            # return Response(
            #     {
            #         'status': 'success',
            #         'message': 'Listing created successfully',
            #         'data': serializer.data,
            #     },
            #     status=status.HTTP_201_CREATED,
            # )
        else:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Error',
                data=serializer.errors,
            )
