from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from ..helpers import handle_exceptions, response


class AboutUser(generics.CreateAPIView):
    '''
    Retrieve and Display User Information
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        user = request.user
        created_at = user.created_at
        created_at = created_at.strftime('%B %Y')

        user_data = {
            'Name': user.name,
            'Created_at': created_at,
        }
        return response(
            status=status.HTTP_200_OK,
            message='User information fetched successfully',
            data=user_data,
        )
