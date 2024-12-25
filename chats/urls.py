'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
End points registry file.
---------------------------------------------------
'''

from django.urls import path

from chats.api.chat import ChatroomListApi, ChatroomDetailApi, CreateChatroomApi
from chats.api.message import MessageListCreateApi

urlpatterns = [
    path('create', CreateChatroomApi.as_view()),
    path(
        'paginate',
        ChatroomListApi.as_view(),
        name='chatroom-list-create',
    ),
    # Get details of a specific chatroom
    path(
        'detail/<str:chat_id>',
        ChatroomDetailApi.as_view(),
        name='chatroom-detail',
    ),
    # Message Management APIs
    # List or send messages in a chatroom
    path(
        'chatrooms/<str:chat_id>/messages/',
        MessageListCreateApi.as_view(),
        name='message-list-create',
    ),
    # # Search messages within a chatroom
    # path(
    #     'chatrooms/<str:chat_id>/messages/search/',
    #     MessageSearchApi.as_view(),
    #     name='message-search',
    # ),
    # path(
    #     'chatrooms/<str:chat_id>/messages/<str:message_id>/read/',
    #     MarkMessageReadApi.as_view(),
    #     name='mark-message-read',
    # ),
    # # Mark a specific message as read
    # # Typing and Read Receipts APIs
    # path(
    #     'chatrooms/<str:chat_id>/typing/',
    #     TypingIndicatorApi.as_view(),
    #     name='typing-indicator',
    # ),
    # # Indicate user typing in a chatroom
    # # Attachments and Media APIs
    # path(
    #     'chatrooms/<str:chat_id>/attachments/',
    #     AttachmentUploadApi.as_view(),
    #     name='attachment-upload',
    # ),
    # # Upload attachments to a chatroom
    # # User-Specific APIs
    # path(
    #     'chatrooms/<str:chat_id>/participants/',
    #     ChatroomParticipantsApi.as_view(),
    #     name='chatroom-participants',
    # ),
    # # Get all participants in a chatroom
    # # List all chat-related notifications for the user
    # path(
    #     'notifications/',
    #     NotificationListApi.as_view(),
    #     name='notifications',
    # ),
    # # Chatroom Analytics APIs (Optional)
    # # Get the count of unread messages across all chatrooms
    # path(
    #     'chatrooms/unread/',
    #     UnreadMessagesCountApi.as_view(),
    #     name='unread-messages-count',
    # ),
    # # Get analytics for a specific chatroom
    # path(
    #     'chatrooms/<str:chat_id>/metrics/',
    #     ChatroomMetricsApi.as_view(),
    #     name='chatroom-metrics',
    # ),
    # # Delete or Archive APIs
    # path(
    #     'chatrooms/<str:chat_id>/archive/',
    #     ArchiveChatroomApi.as_view(),
    #     name='archive-chatroom',
    # ),
    # # Archive a specific chatroom
    # path(
    #     'chatrooms/<str:chat_id>/messages/<str:message_id>/',
    #     DeleteMessageApi.as_view(),
    #     name='delete-message',
    # ),
    # # Delete a specific message in a chatroom
    # # System Settings APIs
    # path(
    #     'chat/settings/', ChatSettingsApi.as_view(), name='chat-settings'
    # ),  # Retrieve or update chat-related system settings
]

# Todo
#   1. /api/chatrooms/  POST
# { "chat_id": "1234"\n"participants": ["user_id1", "user_id2"] }
# Creates a new chatroom or retrieves the existing one for the given participants.
#
#   2. /api/chatrooms/  GET
# [ { "chat_id": "1234", "participants": ["user_id1", "user_id2"], "last_message": "Hi!" } ]
# Lists all chatrooms for the authenticated user.
#
# Message Management APIs
# Send Message
#
# Endpoint: POST /api/chatrooms/<chat_id>/messages/
# Payload: { "content": "Hello, world!" }
# Response: { "message_id": "5678", "chat_id": "1234", "content": "Hello, world!", "sender_id": "user_id", "created_at": "timestamp" }
# Description: Sends a message to the chatroom.
# Fetch Messages
#
# Endpoint: GET /api/chatrooms/<chat_id>/messages/
# Query Params: ?before=<timestamp>&limit=20
# Response: [ { "message_id": "5678", "content": "Hello!", "sender_id": "user_id", "created_at": "timestamp" } ]
# Description: Fetches messages from a chatroom, paginated for infinite scrolling.
#     Search Messages
#
# Endpoint: GET /api/chatrooms/<chat_id>/messages/search/
# Query Params: ?q=<keyword>
# Response: [ { "message_id": "5678", "content": "Search result!" } ]
# Description: Searches for messages in a chatroom based on a keyword.
# 3. Attachments and Media APIs
# Upload Attachment
# Endpoint: POST /api/chatrooms/<chat_id>/attachments/
# Payload: { "file": <file> }
# Response: { "file_url": "https://..." }
# Description: Uploads an attachment or media file to the chatroom.
# 4. Typing and Read Receipts APIs
# Typing Indicator
#
# Endpoint: POST /api/chatrooms/<chat_id>/typing/
# Payload: { "status": "start" | "stop" }
# Response: { "status": "success" }
# Description: Updates typing status for a chatroom.
#     Mark Message as Read
#
# Endpoint: POST /api/chatrooms/<chat_id>/messages/<message_id>/read/
# Response: { "status": "success" }
# Description: Marks a message as read.
# 5. User-Specific APIs
# Fetch Participants
#
# Endpoint: GET /api/chatrooms/<chat_id>/participants/
# Response: [ { "user_id": "user_id1", "name": "John Doe" } ]
# Description: Retrieves the list of participants in a chatroom.
# Fetch Notifications
#
# Endpoint: GET /api/notifications/
# Response: [ { "notification_id": "123", "content": "New message", "read": false } ]
# Description: Retrieves notifications for the authenticated user.
# 6. Chatroom Analytics APIs (Optional)
# Fetch Unread Messages Count
#
# Endpoint: GET /api/chatrooms/unread/
# Response: { "unread_count": 5 }
# Description: Fetches the total number of unread messages for the user.
#     Fetch Chatroom Metrics
#
# Endpoint: GET /api/chatrooms/<chat_id>/metrics/
# Response: { "total_messages": 100, "active_participants": 2 }
# Description: Provides analytics for a chatroom.
#     7. Delete or Archive APIs
# Archive Chatroom
#
# Endpoint: POST /api/chatrooms/<chat_id>/archive/
# Response: { "status": "archived" }
# Description: Archives a chatroom for the user.
#     Delete Message
#
# Endpoint: DELETE /api/chatrooms/<chat_id>/messages/<message_id>/
# Response: { "status": "deleted" }
# Description: Deletes a message from a chatroom.
# 8. System Settings APIs
# Fetch Chat Settings
# Endpoint: GET /api/chat/settings/
# Response: { "max_file_size": 10, "message_retention_days": 30 }
# Description: Retrieves system-wide settings for the chat.
#     Next Steps
# Select the APIs you need based on your features.
# Implement them using Django REST Framework.
# Ensure integration with your WebSocket-based real-time updates for a hybrid solution.
# Let me know if you want help with any specific API!
