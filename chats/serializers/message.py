from rest_framework_mongoengine import serializers
from chats.models.message import Message
from .chat import ChatSerializer

# To include chat details if needed


class MessageSerializer(serializers.DocumentSerializer):
    # chat = ChatSerializer(read_only=True)
    # sender_id = serializers.CharField()

    class Meta:
        model = Message
        fields = ['chat', 'sender_id', 'content', 'read', 'created_at']
