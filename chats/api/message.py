'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Message endpoints.
---------------------------------------------------
'''

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from chats.models import Message, Chat
from chats.serializers import MessageSerializer

from listings.api.paginate_listing import Pagination
from config import AZURE_ACCOUNT_NAME, AZURE_CONTAINER_NAME
from helpers import response, handle_exceptions, blob_service_client


def upload_media(chatroom_id, file):
    '''
    Handles the uploading of media to Azure Blob Storage.
    Returns path to uploaded media.
    '''
    # Generate unique file name and upload
    file_name = f'chats/{chatroom_id}/{file.name}'
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=file_name
    )

    blob_client.upload_blob(file, overwrite=True)
    # Generate URL to access the uploaded file
    media_url = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}'
    return media_url


class MessageListCreateApi(generics.ListCreateAPIView):

    serializer_class = MessageSerializer
    pagination_class = Pagination
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get_queryset(self):
        # todo: fix error code ig chatroom is wrong
        chatroom_id = self.kwargs['chat_id']
        user_id = str(self.request.user.id)
        before = self.request.query_params.get('before')
        chatroom = Chat.objects.get(chat_id=chatroom_id)

        # Check if the user is a participant
        participants = chatroom.participants
        if user_id not in participants:
            return response(
                status=status.HTTP_401_UNAUTHORIZED,
                message='You are not a participant in this chatroom.',
                data={},
            )

        queryset = Message.objects.filter(chat=chatroom).order_by('-created_at')
        if before:
            queryset = queryset.filter(created_at__lt=before)
        return queryset

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        media_url = None
        chatroom_id = kwargs['chat_id']
        user_id = str(request.user.id)
        file = request.FILES.get('file')
        chatroom = Chat.objects.get(chat_id=chatroom_id)
        # Check if the user is a participant
        participants = chatroom.participants
        if user_id not in participants:
            return response(
                status=status.HTTP_401_UNAUTHORIZED,
                message='You are not a participant in this chatroom.',
                data=request.data,
            )
        data = request.data.copy()
        if file:
            media_url = upload_media(chatroom_id, file)
            data['media_url'] = media_url
        data['chat'] = chatroom.id
        data['sender_id'] = user_id
        data['created_at'] = timezone.now()
        # Set the current timestamp
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status=status.HTTP_201_CREATED,
            message='Message sent successfully',
            data=serializer.data,
        )


class MarkMessagesReadApi(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        chat_id = kwargs['chat_id']
        user_id = str(request.user.id)
        chatroom = Chat.objects.get(chat_id=chat_id)
        # Check if the user is a participant
        if user_id not in chatroom.participants:
            return response(
                status=status.HTTP_403_FORBIDDEN,
                message='You are not a participant in this chatroom.',
                data=request.data,
            )

        # Get the messages from the other participant (not the current user)
        # Filter messages that are not sent by the current user
        messages_to_mark_as_read = Message.objects.filter(
            chat=chatroom,
            read=False,
            sender_id__ne=user_id,
        )
        if not messages_to_mark_as_read.exists():
            return response(
                status=status.HTTP_200_OK,
                message='No messages to mark as read.',
                data={'status': 'success'},
            )

        # Mark those messages as read
        messages_to_mark_as_read.update(read=True)
        return response(
            status=status.HTTP_200_OK,
            message='Successfully Marked messages as read',
            data={'status': 'success'},
        )


class DeleteMessageApi(APIView):
    '''
    API to delete a specific message by its ID within a chatroom.
    '''

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def delete(self, request, chat_id, message_id, *args, **kwargs):
        '''
        Deletes a specific message if the user has permission.
        '''
        user_id = str(request.user.id)

        # Fetch the chatroom
        chatroom = Chat.objects.filter(chat_id=chat_id).first()
        if chatroom is None:
            return response(
                status=status.HTTP_404_NOT_FOUND,
                message='Chatroom not found.',
                data={},
            )

        # Check if the user is a participant in the chatroom
        if user_id not in chatroom.participants:
            return response(
                status=status.HTTP_401_UNAUTHORIZED,
                message='You are not a participant in this chatroom.',
                data=request.data,
            )

        # Fetch the message
        message = Message.objects.filter(id=message_id, chat=chatroom).first()
        if not message:
            return response(
                status=status.HTTP_404_NOT_FOUND,
                message='Message not found.',
                data={},
            )

        # Check if the user is the sender of the message
        if message.sender_id != user_id:
            return response(
                status=status.HTTP_403_FORBIDDEN,
                message='You can only delete your own messages.',
                data={},
            )

        # Delete the message
        message.delete()

        return response(
            status=status.HTTP_200_OK,
            message='Message deleted successfully.',
            data={},
        )
