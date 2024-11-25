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
from rest_framework_mongoengine import serializers


class ListsyncSerializer(serializers.DocumentSerializer):

    class Meta:
        model = ListSync
        fields = '__all__'

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
