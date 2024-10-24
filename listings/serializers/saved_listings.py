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

from django.utils import timezone
from listings.models import SavedItem
from listings.helpers.constants import CATEGORIES
from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError


class SavedItemSerializer(serializers.DocumentSerializer):
    class Meta:
        model = SavedItem

    def validate(self, data):
        user = self.context['request'].user
        data['user_id'] = user.id
        category = data.get('category')
        if category not in CATEGORIES:
            raise ValidationError(
                {'category': f'categories should be {CATEGORIES}'}
            )
        data['saved_at'] = timezone.now()
        return data

    def create(self, validated_data):
        return SavedItem.objects.create(**validated_data)
