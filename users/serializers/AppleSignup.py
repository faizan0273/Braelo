from ..models.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError




class AppleSignup(serializers.Serializer):
    '''
    CRUD operation for User.
    '''

    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    google_id = serializers.CharField(
        min_length=11, max_length=255, required=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    is_email_verified = serializers.BooleanField(default=False)
    is_phone_verified = serializers.BooleanField(default=False)

    def validate(self, data):
        '''
        Check that the email or phone number is not already taken.
        '''
        # directories
        email = data['']
        email = data.get('email')
        google_id = data.get('google_id')
        if email and User.objects.filter(email=email).first():
            raise ValidationError({'email': 'This email is already taken.'})

        if google_id and User.objects.filter(google_id=google_id).first():
            raise ValidationError(
                {'google_id': 'This Google ID is already taken.'}
            )
        return data

    def create(self, validated_data):
        if validated_data:
            validated_data['created_at'] = timezone.now()
            validated_data['updated_at'] = timezone.now()
            validated_data['is_active'] = True
            user = User.objects.create_user(**validated_data)
            return user
            # return True
        return False

    def update(self, google_user, **kwargs):
        '''
        Update the user details if any of the provided updated_user_data
        differ from the existing data in the user object.
        :param google_user: Dictionary containing updated user data from Google.(dict)
        :return:
        '''
        user = User.objects.filter(email=google_user['email']).first()
        is_updated = (
            user.name != google_user['name']
            or user.first_name != google_user['first_name']
            or user.last_name != google_user['last_name']
            or user.is_email_verified != google_user['is_email_verified']
            or user.google_id != google_user['google_id']
        )
        if is_updated:
            user.name = google_user['name']
            user.first_name = google_user['first_name']
            user.last_name = google_user['last_name']
            user.is_email_verified = google_user['is_email_verified']
            user.google_id = google_user['google_id']
            user.updated_at = timezone.now()
            user.save()
        return user
