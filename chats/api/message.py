from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action

from chats.models import Message, Chat
from chats.serializers.message import MessageSerializer


class MessageListCreateApi(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat__chat_id=chat_id)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(chat_id=chat_id)
        serializer.save(chat=chat, sender_id=self.request.user.id)


class MarkMessageReadApi(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_object(self):
        message_id = self.kwargs['message_id']
        return Message.objects.get(id=message_id)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.read = True
        message.save()
        return Response({'status': 'Message marked as read'})
