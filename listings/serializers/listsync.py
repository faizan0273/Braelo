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
