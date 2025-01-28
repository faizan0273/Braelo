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

import json
import shortuuid
from mongoengine import Q
from django.utils import timezone
from users.models import User, Business
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
            receiver = record.get('receiver')
            receiver_id = receiver.get('user_id')
            sender = record.get('sender')
            sender_id = sender.get('user_id')

            # finding out who is the online user
            # And getting the second user for searching of their records
            if str(receiver_id) == user_id:
                user_type = sender.get('user_type')
            elif str(sender_id) == user_id:
                user_type = receiver.get('user_type')

            if user_type == 'user':
                second_user = User.objects.filter(id=second_user_id).first()
            else:
                second_user = Business.objects.filter(
                    user_id=second_user_id
                ).first()

            messages_count = messages.count()
            last_message = messages.filter().first()

            if user_type == 'user':
                record['user_picture'] = second_user.profile_picture
                record['user_name'] = second_user.name

            elif user_type == 'business':
                record['business_picture'] = second_user.business_logo
                record['business_name'] = second_user.business_name
            else:
                record['user_picture'] = []
                record['user_name'] = []

            record['unread_messages'] = messages_count

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

    def validate_ids(self, receiver, sender, user_id, second_user_id):
        '''
        validate and storing user and second user ids
        '''

        required_key = 'user_type'
        receiver['user_id'] = second_user_id
        sender['user_id'] = user_id

        if not isinstance(receiver, dict) or not isinstance(sender, dict):
            raise ValidationError(
                {'detail': 'receiver and sender must be valid dictionaries'}
            )
        if str(receiver.get('user_id')) == user_id:
            raise ValidationError({'detail': 'sender cannot be receiver'})

        # Check if the key is missing in either receiver or sender
        if required_key not in receiver:
            raise ValidationError(
                {'message_receiver': f'{required_key} is required in receiver'}
            )
        if required_key not in sender:
            raise ValidationError(
                {'message_receiver': f'{required_key} is required in sender'}
            )

    def get_chatroom(self, user_id, second_user_id, receiver_type, sender_type):
        '''
        Check if a chatroom exists for the two participants.
        '''
        chatroom = Chat.objects.filter(
            participants__all=[user_id, second_user_id],
            receiver__user_type=receiver_type,
            sender__user_type=sender_type,
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
        # checking if data is received in dict
        try:
            receiver = json.loads(request.data.get('receiver'))
            sender = json.loads(request.data.get('sender'))
        except json.JSONDecodeError as exc:
            raise ValidationError(
                {'detail': 'Invalid JSON for receiver or sender.'}
            ) from exc

        if not second_user_id:
            raise ValidationError({'detail': 'Second user ID is required.'})

        self.validate_ids(receiver, sender, user_id, second_user_id)
        receiver_type = receiver.get('user_type')
        sender_type = sender.get('user_type')

        user_exist = User.objects.filter(id=second_user_id).exists()
        if not user_exist:
            raise ValidationError({'id': 'User does not exists'})

        chatroom = self.get_chatroom(
            user_id, second_user_id, receiver_type, sender_type
        )

        if chatroom:
            return response(
                status=status.HTTP_200_OK,
                message='Chat fetched successfully',
                data=ChatSerializer(chatroom).data,
            )

        # If the chatroom doesn't exist, create a new one
        new_chatroom = Chat(
            receiver=receiver,
            sender=sender,
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
        user_type = self.request.GET.get('user_type')
        if not user_type:
            raise ValidationError(
                {'user_type': 'Type must be user or business'}
            )

        query = Q(receiver__user_id=user_id, receiver__user_type=user_type) | Q(
            sender__user_id=user_id, sender__user_type=user_type
        )

        # will return chatrooms based on the user status at the time of creation
        return Chat.objects.filter(query)


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
