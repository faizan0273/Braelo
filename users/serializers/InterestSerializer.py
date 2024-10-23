from ..helpers import INTERESTS
from mongoengine import DoesNotExist
from rest_framework import serializers
from ..models.interests import Interest
from rest_framework.serializers import ValidationError



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