'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User password management end-points module.
---------------------------------------------------
'''

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from Braelo.users.helpers import handle_exceptions
from Braelo.users.serializers import (
    ForgotPasswordSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)


class ResetPassword(generics.CreateAPIView):
    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password reset successful.'},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Ensure the user is authenticated
    serializer_class = ForgotPasswordSerializer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle forgotten password.
        :param request: request object. (dict)
        :return: user's password status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        user.save()
        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK,
        )


class ChangePassword(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user change password on applications.
        :param request: request object. (dict)
        :return: user's password status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        # our logic
        # Generate password reset token
        # token = default_token_generator.make_token(user)
        # uid = urlsafe_base64_encode(force_bytes(user.pk))
        #
        # # Construct password reset URL (You should implement the frontend link handling)
        # reset_url = f'http://yourfrontend.com/reset-password/{uid}/{token}/'
        #
        # # Send email (You can replace `send_mail` with your custom email service)
        # send_mail(
        #     subject='Password Reset',
        #     message=f'Click the link to reset your password: {reset_url}',
        #     from_email='noreply@yourdomain.com',
        #     recipient_list=[email],
        # )
        #
        # return Response(
        #     {'message': 'Password reset link has been sent to your email.'},
        #     status=status.HTTP_200_OK,
        # )
