# todo : Make helper functions for firebase
# import requests
# import firebase_admin
# from firebase_admin import credentials, messaging
#
# from notifications.models import Notification
# from users.models import UserDeviceToken

#
# # Initialize Firebase App
# cred = credentials.Certificate(
#     '/home/muhammad/Desktop/FL/FL/Braelo/credentials.json'
# )
# firebase_admin.initialize_app(cred)
#
#
# def send_push_notification(user, title, body, data=None):
#     '''
#     Sends a push notification to the user's devices using Firebase.
#     '''
#     device_tokens = UserDeviceToken.objects.filter(user=user).values_list(
#         'token', flat=True
#     )
#     if not device_tokens:
#         return
#
#     FCM_SERVER_KEY = 'YOUR_FCM_SERVER_KEY'
#     headers = {
#         'Authorization': f'key={FCM_SERVER_KEY}',
#         'Content-Type': 'application/json',
#     }
#     payload = {
#         'registration_ids': list(device_tokens),
#         'notification': {'title': title, 'body': body, 'sound': 'default'},
#         'data': data or {},
#     }
#     response = requests.post(
#         'https://fcm.googleapis.com/fcm/send', headers=headers, json=payload
#     )
#     return response.json()
#
#
# def send_fcm_notification(user_id, title, body):
#     '''
#     Send FCM notification to a specific user.
#     '''
#     # Get the user's device tokens
#     tokens = UserDeviceToken.objects.filter(user_id=user_id).values_list(
#         'token', flat=True
#     )
#
#     if not tokens:
#         return {
#             'success': False,
#             'message': 'No device tokens found for the user',
#         }
#
#     # Create the FCM message
#     message = messaging.MulticastMessage(
#         tokens=list(tokens),
#         notification=messaging.Notification(
#             title=title,
#             body=body,
#         ),
#     )
#
#     # Send the message and handle the response
#     response = messaging.send_multicast(message)
#     return {
#         'success': True,
#         'message': f'{response.success_count} messages sent.',
#     }


# def initialize_firebase(cred_path):
#     cred = credentials.Certificate(cred_path)
#     if not firebase_admin._apps:
#         # Avoid initializing multiple times
#         firebase_admin.initialize_app(cred)

#
# def send_notification(title, body, recipient_tokens):
#     # Send notification via Firebase
#     message = messaging.MulticastMessage(
#         notification=messaging.Notification(title=title, body=body),
#         tokens=recipient_tokens,
#     )
#
#     response = messaging.send_multicast(message)
#     failed_tokens = [
#         recipient_tokens[idx]
#         for idx, resp in enumerate(response.responses)
#         if not resp.success
#     ]
#
#     # Log or handle failed tokens
#     if failed_tokens:
#         print("Failed tokens:", failed_tokens)
#
#     return response.success_count
#
#
# def create_and_send_notification(title, body, recipient_tokens):
#     # Store notification
#     notification = Notification(
#         title=title,
#         body=body,
#         recipient_ids=recipient_tokens,
#     )
#     notification.save()
#
#     # Send notification via FCM
#     success_count = send_notification(title, body, recipient_tokens)
#
#     # Mark as sent if successful
#     if success_count > 0:
#         notification.mark_as_sent()
#
#     return success_count

SAVED_EVENT_DATA = {
    'type': 'chat',
    'title': 'New message received',
    'body': 'Listings saved succesfully',
    'data': {'listing_id': ''},
    'user_id': [],
}

BUSSINESS_EVENT_DATA = {
    'type': 'chat',
    'title': 'New message received',
    'body': 'Listings created succesfully',
    'data': {'business_id': '', 'business_type': '', 'user_id': ''},
    'user_id': [],
}
LISTINGS_EVENT_DATA = {
    'type': 'chat',
    'title': 'New message received',
    'body': 'Listings created succesfully',
    'data': {
        # 'listing_id':'',
        'category': '',
        'user_id': '',
    },
    'user_id': [],
}
