'''
@author: Hamid
Date: 14 Aug, 2024
'''

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from Braelo.users.helpers.helper import get_error_details
from Braelo.users.serializers import (
    ForgotPasswordSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)
from django.db import DatabaseError as SQLITE_ERROR


class ResetPassword(generics.CreateAPIView):
    '''
    Reset password Api.
    '''

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
    '''
    Forgot password Api
    '''

    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user.save()
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePassword(generics.CreateAPIView):
    '''
    Change password Api
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
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
            return Response(
                {'message': 'Password reset link has been sent to your email.'},
                status=status.HTTP_200_OK,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            # Email already exists
            return Response(
                {'detail': 'Validation Error', 'errors': error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SQLITE_ERROR as err:
            return Response(
                {'detail': 'Database failure', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {'detail': 'Exception', 'errors': str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
