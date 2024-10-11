from rest_framework import generics, status
from ..serializers import UpdateProfileSerializer
from ..helpers import handle_exceptions, response
from rest_framework.permissions import IsAuthenticated


class UpdateProfile(generics.CreateAPIView):

    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        Handle the Profile Update mechanism
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_data = serializer.save()

        return response(
            status=status.HTTP_200_OK,
            message='Profile updated successfully',
            data=updated_data,
        )
