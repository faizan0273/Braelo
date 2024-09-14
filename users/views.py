import pyotp
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Interest
from .helpers.google_auth import google_auth
from .helpers.decorators import handle_exceptions
from .helpers.helper import get_error_details, get_token, response
from .serializers import (
    EmailSignup,
    EmailLogin,
    PhoneSignup,
    GoogleSignup,
    PhoneLogin,
    AppleSignup,
    ForgotPasswordSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    InterestSerializer,
)


class SignUpWithEmail(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = EmailSignup
    permission_classes = [AllowAny]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user sign up on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        # add username to the validated data
        user.validated_data['username'] = user.validated_data['email']
        user = user.create(user.validated_data)
        if not user:
            # todo: needs better logic
            raise Exception('Cannot Add user to Database')
        # Generate JWT token after user creation
        token = get_token(user)
        # Combine user data with token data
        data = {'email': user.email, 'token': token}
        return response(
            status=status.HTTP_201_CREATED,
            message='User Signed Up',
            data=data,
        )


class SignUpWithPhone(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PhoneSignup
    permission_classes = [AllowAny]

    def _generate_otp(self):
        '''
        generates 6-digits otp code.
        :return: otp code. (int)
        '''
        # Generate the OTP
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, digits=6)
        return totp.now()

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user sign up on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        # todo ph#
        #  1. In case of phone number otp generations
        resp = request.data
        user = self.get_serializer(data=resp)
        user.is_valid(raise_exception=True)
        otp = self._generate_otp()
        user.validated_data['otp'] = otp
        user.validated_data['otp_created_at'] = datetime.now()
        # todo Send OTP to user's phone
        # send_otp_to_phone(user.phone_number, otp)
        # add username to the validated data
        user.validated_data['username'] = user.validated_data['phone_number']
        user = user.create(user.validated_data)
        if not user:
            raise Exception('Cannot Add user to Database')
        # Generate JWT token after user creation
        token = get_token(user)
        # Combine user data with token data
        data = {
            'phone': user.phone_number,
            'token': token,
        }
        return response(
            status=status.HTTP_201_CREATED,
            message='User Signed Up',
            data=data,
        )


class GoogleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = GoogleSignup

    @handle_exceptions
    @csrf_exempt
    def post(self, request):
        '''
        POST method to handle user signup/login on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        token = request.data.get('credential')
        # Google User Details
        g_user = google_auth(token)
        _user = self.get_serializer(data=g_user)
        try:
            _user.is_valid(raise_exception=True)
            # add username to the validated data
            _user.validated_data['username'] = _user.validated_data['email']
            _user = _user.create(_user.validated_data)
            if not _user:
                raise Exception('Cannot Add user to Database')
            # No user is available for this email create new user to our db
            # Generate JWT token after user creation
            token = get_token(_user)
            # Combine user data with token data
            response_data = {'email': _user.email, 'token': token}
            # return Response(response_data, status=status.HTTP_201_CREATED)
            return response(
                status=status.HTTP_201_CREATED,
                message='User Signed Up',
                data=response_data,
            )
        except ValidationError as err:
            error = get_error_details(err.detail)
            if not g_user:
                return response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='Validation Error',
                    data={},
                    error=error,
                )

            # Email already exists
            _user = _user.update(g_user)
            token = get_token(_user)
            response_data = {'email': _user.email, 'token': token}
            return response(
                status=status.HTTP_200_OK,
                message='user logged in',
                data=response_data,
            )


class AppleCallback(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = AppleSignup

    @csrf_exempt
    def post(self, request):
        pass


# login part
class LoginWithPhone(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = PhoneLogin

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user login in on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        user = user.validated_data
        token = get_token(user)
        response_data = {'phone_number': user.phone_number, 'token': token}
        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )


# login part-
class LoginWithEmail(generics.CreateAPIView):
    serializer_class = EmailLogin
    permission_classes = [AllowAny]  # Ensure the user is authenticated

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        POST method to handle user login on applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        data = request.data
        user = self.get_serializer(data=data)
        user.is_valid(raise_exception=True)
        user = user.validated_data
        token = get_token(user)
        response_data = {'email': user.email, 'token': token}
        return response(
            status=status.HTTP_200_OK,
            message='user Logged in',
            data=response_data,
        )


class TokenRefresh(generics.CreateAPIView):
    pass


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


class Logout(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to handle user logout from applications.
        :param request: request object. (dict)
        :return: user's signed up status. (json)
        '''
        # Extract the refresh token from request data
        refresh_token = request.data.get('refresh')
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
        return response(
            status=status.HTTP_200_OK,
            message='Logged out successfully.',
            data={'refresh_token': refresh_token},
            error='',
        )


#
# # List and Create Interest API
# class InterestListCreateView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = InterestSerializer
#     queryset = Interest.objects.all()
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         data['user_id'] = request.user.id
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# # Retrieve, Update, and Delete Interest API
# class InterestDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = InterestSerializer
#     queryset = Interest.objects.all()
#     lookup_field = (
#         'id'  # Use 'id' or '_id' depending on how you're accessing the document
#     )
#


# testing
@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')
