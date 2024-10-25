from ..models.models import User
from rest_framework import serializers

class UserProfileSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'name',
            'first_name',
            'last_name',
            'google_id',
            'apple_id',
            'created_at',
            'updated_at',
            'is_active',
            'is_email_verified',
            'is_phone_verified',
            'role',
        ]
