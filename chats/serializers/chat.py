'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
chat serializer file.
---------------------------------------------------
'''

from rest_framework_mongoengine import serializers

from chats.models import Chat


class ChatSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
