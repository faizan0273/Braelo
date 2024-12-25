import shortuuid
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from chats.models import Chat
from chats.serializers.chat import ChatSerializer

from rest_framework.pagination import PageNumberPagination

from helpers import response


class ChatroomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateChatroomApi(generics.CreateAPIView):
    '''
    API endpoint to either create a new chatroom or retrieve an existing one.
    The chatroom is identified by participants' user IDs.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_chatroom(self, user_id, second_user_id):
        '''
        Check if a chatroom exists for the two participants.
        '''
        chatroom = Chat.objects.filter(
            participants__all=[user_id, second_user_id]
        )
        if chatroom.count() > 0:
            return chatroom.first()
        return None

    def post(self, request, *args, **kwargs):
        '''
        Handle the creation or retrieval of a chatroom.
        '''
        user_id = str(request.user.id)  # Get the current user's ID
        second_user_id = request.data.get('user_id')

        if not second_user_id:
            raise ValidationError({'detail': 'Second user ID is required.'})

        chatroom = self.get_chatroom(user_id, second_user_id)

        if chatroom:
            return response(
                status=status.HTTP_200_OK,
                message='Chat created successfully',
                data=ChatSerializer(chatroom).data,
            )

        # If the chatroom doesn't exist, create a new one
        new_chatroom = Chat(
            participants=[user_id, second_user_id],
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            chat_id=shortuuid.uuid(),
        )
        new_chatroom.save()
        data = ChatSerializer(new_chatroom).data
        return response(
            status=status.HTTP_201_CREATED,
            message='Chat created successfully',
            data=data,
        )


class ChatroomListApi(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = ChatroomPagination

    def get_queryset(self):
        # Filter chatroom's where the user is a participant
        user_id = str(self.request.user.id)
        return Chat.objects.filter(participants__in=[user_id])


class ChatroomDetailApi(generics.RetrieveUpdateDestroyAPIView):

    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']  # Retrieve chat_id from the URL
        return Chat.objects.filter(chat_id=chat_id)

    def get_object(self):
        queryset = self.get_queryset()
        user_id = str(self.request.user.id)
        chat = queryset.filter(participants__in=[user_id]).first()
        if not chat:
            raise NotFound("Chat not found or you are not a participant")
        return chat
