'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Chat endpoint file.
---------------------------------------------------
'''

import shortuuid
from users.models import User
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ValidationError

from chats.models import Chat, Message
from chats.serializers.chat import ChatSerializer

from helpers import response, handle_exceptions


class ChatroomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        user = self.request.user
        user_id = str(user.id)

        paginated_data = super().get_paginated_response(data).data
        paginate_results = paginated_data.get('results')

        for record in paginate_results:
            messages = Message.objects.filter(
                chat=record.get('id'), read=False, sender_id__ne=user_id
            )
            participants = record.get('participants')
            second_user_id = next(val for val in participants if val != user_id)
            second_user = User.objects.filter(id=second_user_id).first()
            messages_count = messages.count()
            last_message = messages.filter().first()

            record['unread_messages'] = messages_count
            record['user_picture'] = (
                second_user.profile_picture if second_user else []
            )
            record['user_name'] = second_user.name if second_user else []
            record['message_created_at'] = (
                last_message.created_at if last_message else []
            )
            record['last_message'] = (
                last_message.content if last_message else []
            )

        paginated_data['results'] = paginate_results

        return response(
            status=status.HTTP_200_OK,
            message='chatrooms fetched Successfully',
            data=paginated_data,
        )


class CreateChatroomApi(generics.CreateAPIView):
    '''
    API endpoint to either create a new chatroom or retrieve an existing one.
    The chatroom is identified by participants' user IDs.
    '''

    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

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

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        '''
        Handle the creation or retrieval of a chatroom.
        '''
        user_id = str(request.user.id)  # Get the current user's ID
        second_user_id = request.data.get('user_id')

        if not second_user_id:
            raise ValidationError({'detail': 'Second user ID is required.'})

        user_exist = User.objects.filter(id=second_user_id).exists()
        if not user_exist:
            raise ValidationError({'id': 'User does not exists'})

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


class DeleteChatroomApi(APIView):
    '''
    API to delete a chatroom and its associated messages.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def delete(self, request, *args, **kwargs):
        chatroom_id = kwargs.get('chat_id')
        user_id = str(request.user.id)
        if not chatroom_id:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Chatroom ID is required in query parameters.',
                data={},
            )
        # Fetch the chatroom
        chatroom = Chat.objects.filter(chat_id=chatroom_id).first()

        if not chatroom:
            return response(
                status=status.HTTP_404_NOT_FOUND,
                message='Chatroom not found.',
                data={},
            )

        if user_id not in chatroom.participants:
            return response(
                status=status.HTTP_403_FORBIDDEN,
                message='You are not authorized to delete this chatroom.',
                data={},
            )

        # Delete all messages in the chatroom
        Message.objects.filter(chat=chatroom).delete()

        # Delete the chatroom
        chatroom.delete()

        return response(
            status=status.HTTP_200_OK,
            message='Chatroom and its messages deleted successfully.',
            data={},
        )


class ChatroomListApi(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = ChatroomPagination

    def get_queryset(self):
        # Filter chatroom's where the user is a participant
        user_id = str(self.request.user.id)
        return Chat.objects.filter(participants__in=[user_id])


class ChatroomDetailApi(generics.ListAPIView):

    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get(self, request, **kwargs):
        chat_id = self.kwargs['chat_id']
        user_id = str(self.request.user.id)
        chat = Chat.objects.filter(
            chat_id=chat_id, participants__in=[user_id]
        ).first()
        chat_data = self.get_serializer(chat)

        return response(
            status=status.HTTP_200_OK,
            message='Chatroom Fetched Successfully',
            data=chat_data.data,
        )
