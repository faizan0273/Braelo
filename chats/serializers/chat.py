from rest_framework_mongoengine import serializers

from chats.models import Chat


class ChatSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
