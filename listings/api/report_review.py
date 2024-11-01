from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from listings.helpers import handle_exceptions, response

from listings.serializers.report_review import (
    ReportIssueSerializer,
    ReviewSerializer,
)


class ReportIssue(generics.CreateAPIView):
    '''
    handles submit a request for any issue
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = ReportIssueSerializer

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


class Review(generics.CreateAPIView):
    '''
    handles creation of review
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    @handle_exceptions
    def post(self, request, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='review submitted successfully',
            data=serializer.data,
        )
