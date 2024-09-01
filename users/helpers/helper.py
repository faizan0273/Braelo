"""
Users helper functions
"""

from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken


def get_error_details(error_info):
    error_message = None
    for key, errors in error_info.items():
        if isinstance(errors, list):
            error_message = str(errors[0]) if errors else 'Unknown error'
            error_message = f'{key}: {error_message}'
        else:
            error_message = f'{key}: {str(errors)}'
    return error_message


def response(status, message, data, error=None):
    """
    Returns a structured response with validation errors.
    :param status: Status code information. (dict)
    :param error: Error information. (dict)
    :param data: User information. (dict)
    :param message: Information about response. (dict)
    :return: Response object with formatted error details.
    """
    if isinstance(data, dict) and not data:
        if data.get('password'):
            data['password'] = '********'
    resp = {
        'status': status,
        'message': message,
        'error': error,
        'data': data,
    }
    return JsonResponse(resp)


def get_token(user):
    # Generate JWT token after user creation
    refresh = RefreshToken.for_user(user)
    token_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return token_data
