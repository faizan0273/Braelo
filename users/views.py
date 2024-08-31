import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from google.auth.exceptions import GoogleAuthError

# Create your views here.
# users/views.py

from rest_framework import generics, permissions, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# from google.auth.transport import requests
# from google.oauth2 import id_token


from .helpers.helper import response, get_error_details
from .models import User
from .serializers import (
    UserSerializer,
    EmailSignup,
    EmailLogin,
    PhoneSignup,
    GoogleSignup,
)
from django.db import DatabaseError as SQLITE_ERROR


def google_user_payload(record):
    """
    Creates our schema payload of Google user.
    :param record: google api information. (dict)
    :return: parsed payload. (dict)
    """
    user = {
        'name': record['name'],
        'email': record['email'],
        'google_id': record['sub'],
        'first_name': record['given_name'],
        'last_name': record['family_name'],
        'is_email_verified': record['email_verified'],
    }
    return user


class SignUpWithEmailView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = EmailSignup
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.create(user.validated_data)
            # user = user.save()  # Save the user instance
            if user:
                # Generate JWT token after user creation
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                # Combine user data with token data
                response_data = {'email': user.email, 'token': token_data}
                return Response(response_data, status=status.HTTP_201_CREATED)
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


class SignUpWithPhone(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PhoneSignup
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # todo ph#
        #  1. In case of phone number otp generations
        data = request.data
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.create(user.validated_data)
            if user:
                # Generate JWT token after user creation
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                # Combine user data with token data
                response_data = {
                    'phone': user.phone_number,
                    'token': token_data,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
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


#
# class GoogleCallbackView(generics.CreateAPIView):
#     @csrf_exempt
#     def post(self, request):
#         token = request.data.get('credential')
#         try:
#             resp = id_token.verify_oauth2_token(
#                 token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
#             )
#         except ValueError as exc:
#             return Response(
#                 {'detail': 'Value Error', 'errors': str(exc)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         except GoogleAuthError as exc:
#             return Response(
#                 {'detail': 'GoogleAuthError', 'errors': str(exc)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         # Google User Details
#         g_user = google_user_payload(resp)
#         try:
#             _user = GoogleSignup(data=g_user)
#             _user.is_valid(raise_exception=True)
#
#             # No user is available for this email create new user to our db
#             if _user.create(_user.validated_data):
#                 return Response(
#                     {'message': 'User Created', 'user': g_user},
#                     status=status.HTTP_201_CREATED,
#                 )
#
#         except ValidationError as err:
#             error = get_error_details(err.detail)
#             if not g_user:
#                 return Response(
#                     {'detail': 'Validation Failed', 'errors': error},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             # Email already exists
#             db_payload = User.objects(email=g_user['email']).first()
#             if _user.update(db_payload, g_user):
#                 return Response(
#                     {'message': 'User Updated', 'user': g_user},
#                     status=status.HTTP_200_OK,
#                 )
#
#             # No changes found
#             return Response(
#                 {'message': 'User Logged In', 'user': g_user},
#                 status=status.HTTP_304_NOT_MODIFIED,
#             )
#
#         except SQLITE_ERROR as err:
#             return Response(
#                 {'detail': 'Database failure', 'errors': str(err)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         except Exception as err:
#             return Response(
#                 {'detail': 'Exception', 'errors': str(err)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#
# @csrf_exempt
# @api_view(['POST'])
# def google_callback(request):
#     token = request.POST['credential']
#     try:
#         resp = id_token.verify_oauth2_token(
#             token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
#         )
#     except ValueError as exc:
#         return response(
#             status.HTTP_400_BAD_REQUEST, 'Value Error', '', str(exc)
#         )
#     except GoogleAuthError as exc:
#         return response(
#             status.HTTP_400_BAD_REQUEST, 'GoogleAuthError', '', str(exc)
#         )
#     # Google User Details
#     g_user = google_user_payload(resp)
#     try:
#         _user = GoogleSignup(data=g_user)
#         _user.is_valid(raise_exception=True)
#         # No user is available for this email create new user to our db
#         if _user.create(_user.validated_data):
#             return response(status.HTTP_201_CREATED, 'User Created', g_user)
#     except ValidationError as err:
#         error = get_error_details(err.detail)
#         if not g_user:
#             return response(
#                 status.HTTP_400_BAD_REQUEST, 'Validation Failed', g_user, error
#             )
#         # Email already exist
#         # update the new document if changes
#         db_payload = User.objects(email=g_user['email']).first()
#         if _user.update(db_payload, g_user):
#             # user updated
#             return response(status.HTTP_200_OK, 'User Updated', g_user)
#         # No changes found
#         return response(
#             status.HTTP_304_NOT_MODIFIED,
#             'User Logged In',
#             g_user,
#         )
#     except SQLITE_ERROR as err:
#         return Response(
#             {'detail': 'Database failure', 'errors': str(err)},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     except Exception as err:
#         return Response(
#             {'detail': 'Exception', 'errors': str(err)},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#


# login part
class LoginWithEmailView(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = []  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        try:
            user = self.get_serializer(data=data)
            user.is_valid(raise_exception=True)
            user = user.validated_data
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': user.role,  # Include the role in the response if needed
                },
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


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_jwt(request):
    # Create an instance of JWTAuthentication
    jwt_auth = JWTAuthentication()
    try:
        # Attempt to authenticate the request
        user, auth = jwt_auth.authenticate(request)
        # If authentication is successful, return status 200
        if user:
            return response(status.HTTP_200_OK, "verified", user)
    except AuthenticationFailed:
        # If authentication fails, return a 401 Unauthorized response
        return response(status.HTTP_401_UNAUTHORIZED, "not verified", {})


@api_view(['GET'])
# @permission_classes([AllowAny])
def verify_me(request):
    return Response({"message": "Hi"}, status=status.HTTP_200_OK)
