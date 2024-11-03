'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User Feedbacks/review Endpoints.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from helpers import handle_exceptions, response

from feedbacks.serializers import RequestsSerializer, FeedbacksSerializer


class Requests(generics.CreateAPIView):
    '''
    User requests form endpoint.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = RequestsSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Request Submitted Successfully',
            data=serializer.data,
        )


class Feedback(generics.CreateAPIView):
    '''
    User feedback endpoint.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = FeedbacksSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Feedback submitted successfully',
            data=serializer.data,
        )
