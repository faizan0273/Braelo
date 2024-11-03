'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
google auth helper functions file.
---------------------------------------------------
'''

import os

from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError

from rest_framework.response import Response

GOOGLE_OAUTH_CLIENT_ID = (
    "221272028067-cnm21hi90qmfp0jggj62148fetbv8qbn.apps.googleusercontent.com"
)


def google_user_payload(record):
    '''
    Creates our schema payload of Google user.
    :param record: google api information. (dict)
    :return: parsed payload. (dict)
    '''
    user = {
        'name': record['name'],
        'email': record['email'],
        'google_id': record['sub'],
        'first_name': record['given_name'],
        'last_name': record['family_name'],
        'is_email_verified': record['email_verified'],
    }
    return user


def google_auth(token):
    '''
    Verify google credentials.
    :param token: token information from front-end. (string)
    :return: google api response. (dict)
    '''
    try:
        resp = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID
        )
        return google_user_payload(resp)
    except (ValueError, GoogleAuthError) as exc:
        return Response(
            {'detail': 'GoogleAuthError', 'errors': str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
