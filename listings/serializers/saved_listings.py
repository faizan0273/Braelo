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
from helpers.constants import CATEGORIES
from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError

from listings.api import MODEL_MAP 

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
        validation_data ={
            'id': data.get('listing_id'),
            'title': data.get('title'),
            'price': data.get('price'),
            'location': data.get('location')
        }

        model = MODEL_MAP.get(category)
        if not model.objects.filter(**validation_data):
            raise ValidationError(
                {'listings': 'Data Invalid or no matching listings found'}
            )

        data['saved_at'] = timezone.now()
        return data

    def create(self, validated_data):
        return SavedItem.objects.create(**validated_data)
