'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------
Description:
Serializer file for users based endpoints
---------------------------------------------------
'''

from mongoengine import DoesNotExist
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from django.utils import timezone
from helpers import INTERESTS
from users.models import Interest, User


class InterestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    def validate_tags(self, tags):
        '''
        Check if the provided tags are correct.
        :param tags: tags from request. (list)
        :return: return tags If it exists | exception. (list)
        '''
        for tag in tags:
            if tag not in INTERESTS:
                raise ValidationError({'tags': 'Incorrect tag.'})
        return tags

    def validate_user_id(self, user_id):
        '''
        Check if the user_id already exists.
        :param user_id: id of user from mysql db. (int)
        :return: If it exists, return the existing object for update | user_id.
        '''
        try:
            # If user_id exists, return the corresponding Interest object (for updating)
            interest = Interest.objects.get(user_id=user_id)
            return interest
        except DoesNotExist:
            # If user_id does not exist, return the user_id (for creating a new entry)
            return user_id

    def create(self, validated_data):
        '''
        Create a new interest record for a user if it doesn't already exist.
        '''
        return Interest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''
        Update the existing interest record for a user.
        '''
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance

    def save(self, **kwargs):
        '''
        Save or update the user interest based on whether the user_id exists.
        '''
        interest = self.validated_data.get('user_id')
        if isinstance(interest, Interest):
            # If the validate_user_id returned an existing object, update it
            return self.update(interest, self.validated_data)
        else:
            # Otherwise, create a new interest
            return self.create(self.validated_data)


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    gender = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    complement = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)

    def validate(self, data):
        '''
        Verify the provided email exists.
        '''
        user = self.context['request'].user
        email = data.get('email')
        phone = data.get('phone')
        name = data.get('name')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        dob = data.get('dob')
        gender = data.get('gender')
        address = data.get('address')
        complement = data.get('complement')
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')
        zip_code = data.get('zip_code')
        # If the user already has an email, they can't add one
        if email and phone:
            raise ValidationError(
                'Only one of email or phone should be provided.'
            )
        if email:
            if user.email:
                raise ValidationError(
                    {'email': 'Email is already set and cannot be changed.'}
                )
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    {'email': 'This email is already in use.'}
                )
        # If the user already has a phone number, they can't add one
        if phone:
            if user.phone_number:
                raise ValidationError(
                    {
                        'phone': 'Phone number is already set and cannot be changed.'
                    }
                )
            if User.objects.filter(phone_number=phone).exists():
                raise ValidationError(
                    {'phone': 'This phone number is already in use.'}
                )
        # todo dob, gender, address, complement , country, state, city, Zip code
        if name and user.name == name:
            raise ValidationError({'name': 'Already same.'})
        if first_name and user.first_name == first_name:
            raise ValidationError({'first_name': 'Already same.'})
        if last_name and user.last_name == last_name:
            raise ValidationError({'last_name': 'Already same.'})
        if dob and user.dob == dob:
            raise ValidationError({'date_of_birth': 'Already same.'})
        if gender and user.gender == gender:
            raise ValidationError({'gender': 'Already same.'})
        if address and user.address == address:
            raise ValidationError({'address': 'Already same.'})
        if complement and user.complement == complement:
            raise ValidationError({'complement': 'Already same.'})
        if country and user.country == country:
            raise ValidationError({'country': 'Already same.'})
        if state and user.state == state:
            raise ValidationError({'state': 'Already same.'})
        if city and user.city == city:
            raise ValidationError({'city': 'Already same.'})
        if zip_code and user.zip_code == zip_code:
            raise ValidationError({'zip_code': 'Already same.'})
        return data

    def save(self, **kwargs):
        '''
        Save or update the profile fields provided by user.
        '''
        user = self.context['request'].user
        validated_data = self.validated_data
        if not validated_data:
            return {}
        # Update user fields if present in validated_data
        update_fields = [
            'email',
            'phone',
            'name',
            'first_name',
            'last_name',
            'dob',
            'gender',
            'address',
            'complement',
            'country',
            'state',
            'city',
            'zip_code',
        ]
        for field in update_fields:
            if field in validated_data:
                setattr(user, field, validated_data[field])
        # # Update the missing information
        # if validated_data.get('email'):
        #     user.email = validated_data['email']
        # if validated_data.get('phone'):
        #     user.phone_number = validated_data['phone']
        # user.name = validated_data.get('name', user.name)
        # user.first_name = validated_data.get('first_name', user.first_name)
        # user.last_name = validated_data.get('last_name', user.last_name)
        user.save()
        return validated_data


class UserProfileSerializer(serializers.ModelSerializer):
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
            'dob',
            'gender',
            'address',
            'complement',
            'country',
            'state',
            'city',
            'zip_code',
        ]


class DeactivateUserSerializer(serializers.Serializer):

    def validate(self, data):
        # Check if the user is already inactive.
        user = self.context['request'].user
        # Mark as inactive and add an update timestamp.
        if not user.is_active:
            raise ValidationError(
                {'user': 'This profile is already deactivated.'}
            )
        data['is_active'] = False
        data['updated_at'] = timezone.now()
        return data

    def save(self, **kwargs):
        # Deactivate the user and update the timestamp.
        user = self.context['request'].user
        user.is_active = False
        user.updated_at = self.validated_data['updated_at']
        user.save()
        return {'user_id': user.id, 'is_active': user.is_active}
