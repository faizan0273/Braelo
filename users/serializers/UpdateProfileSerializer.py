from rest_framework import serializers
from rest_framework.serializers import ValidationError


        
class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate(self, data):
        '''
        Verify the provided email exists.
        '''

        user = self.context['request'].user
        name = data.get('name')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if name and user.name == name:
            raise ValidationError({'name': 'The name is already the same.'})
        if first_name and user.first_name == first_name:
            raise ValidationError(
                {'first_name': 'The first name is already the same.'}
            )
        if last_name and user.last_name == last_name:
            raise ValidationError(
                {'last_name': 'The last name is already the same.'}
            )
        return data

    def save(self, **kwargs):
        '''
        Save or update the profile fields provided by user.
        '''
        user = self.context['request'].user
        validated_data = self.validated_data
        if not validated_data:
            return {}
        user.name = validated_data.get('name', user.name)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.save()
        return validated_data