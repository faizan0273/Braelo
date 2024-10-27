'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Helper functions file.
---------------------------------------------------
'''

from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile


def get_error_details(error_info):
    '''
    gets Error message through exceptions.
    :param error_info: exception error. (dict)
    :return: error information. (string)
    '''
    error_message = None
    for key, errors in error_info.items():
        if isinstance(errors, list):
            error_message = str(errors[0]) if errors else 'Unknown error'
            error_message = f'{key}: {error_message}'
        else:
            error_message = f'{key}: {str(errors)}'
    return error_message


def response(status, message, data, error=None):
    '''
    Returns a structured response with validation errors.
    :param status: Status code information. (dict)
    :param error: Error information. (dict)
    :param data: User information. (dict)
    :param message: Information about response. (dict)
    :return: Response object with formatted error details.
    '''

    def clean_data(data):
        resp = {}
        for key, value in data.items():
            if not isinstance(value, InMemoryUploadedFile):
                resp[key] = value
            else:
                resp[key] = value.name
        return resp

    if isinstance(data, list):
        data = [clean_data(item) for item in data]
    elif isinstance(data, dict):
        data = clean_data(data)

    resp = {
        'status': status,
        'message': message,
        'error': error,
        'data': data,
    }
    return JsonResponse(resp)
