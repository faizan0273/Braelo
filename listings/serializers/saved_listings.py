'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for saved item Listings based endpoints
---------------------------------------------------
'''

from bson import ObjectId
from bson.errors import InvalidId
from django.utils import timezone
from listings.models import SavedItem
from helpers.constants import CATEGORIES
from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError

from listings.api import MODEL_MAP


class SavedItemSerializer(serializers.DocumentSerializer):
    class Meta:
        model = SavedItem

    def validate_id(self, value):
        """
        Ensure the `id` field is a valid ObjectId.
        """
        try:
            ObjectId(value)  # Validate the format of the provided ID
        except InvalidId:
            raise ValidationError("Invalid listing ID format.")
        return value

    def validate(self, data):
        '''
        Additional validation for the SavedItem.
        '''
        user = self.context['request'].user
        data['user_id'] = user.id

        # Validate category
        category = data.get('category')
        if category not in CATEGORIES:
            raise ValidationError(
                {
                    'category': f'Invalid category. Available categories: {CATEGORIES.keys()}'
                }
            )

        # Ensure the listing exists
        validation_data = {
            'id': data['id'],
            'title': data['title'],
            'price': data['price'],
            'location': data['location'],
        }
        model = MODEL_MAP.get(category)
        if not model.objects.filter(**validation_data):
            raise ValidationError(
                {'listings': 'Data Invalid or no matching listings found'}
            )

        # Add `saved_at` timestamp
        data['saved_at'] = timezone.now()
        return data

    def create(self, validated_data):
        '''
        Create a SavedItem document.
        '''
        return SavedItem.objects.create(**validated_data)
