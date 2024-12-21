'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User Login end-points module.
---------------------------------------------------
'''

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

from helpers import handle_exceptions, response
from users.serializers.devices import DeviceTokenSerializer


class SaveDeviceToken(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DeviceTokenSerializer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to save user device token.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        data['user_id'] = request.user.id
        serializer = self.get_serializer(
            data=data, context={'request': request}
        ) 
        serializer.is_valid(raise_exception=True)
        resp = serializer.save()
        if not resp:
            # todo: needs better logic
            raise Exception('Cannot Add interests to Database')
        return response(
            status=status.HTTP_201_CREATED,
            message='Device token Added successfully.',
            data=data,
        )
