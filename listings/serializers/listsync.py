'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for list sync Listings based endpoints
---------------------------------------------------
'''

from helpers.models.listsync import ListSync
from rest_framework import serializers as SE
from rest_framework_mongoengine import serializers

from listings.models import SavedItem


class ListsyncSerializer(serializers.DocumentSerializer):
    is_saved = SE.SerializerMethodField()

    class Meta:
        model = ListSync
        fields = '__all__'

    def get_is_saved(self, obj):
        """
        Check if the listing is saved by the current user.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        # Assuming SavedItem has fields: `user_id` and `listing_id`
        return bool(SavedItem.objects(user_id=user.id, id=obj.id))

    def to_representation(self, instance):
        '''
        Modify 'fields attribute' to exclude NULL fields of Mongo doc
        '''
        modify_fields = super().to_representation(instance)

        # Remove values from fields if price or salary is NULL
        if instance.price is None:
            modify_fields.pop('price', None)
        if instance.salary_range is None:
            modify_fields.pop('salary_range', None)
        return modify_fields
