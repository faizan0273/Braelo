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

import hashlib

from django.http import JsonResponse


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

    resp = {
        'status': status,
        'message': message,
        'error': error,
        'data': data,
    }
    return JsonResponse(resp)


def _upload_to_s3(self, data):
    """
    Upload data on s3.
    @param data: Object name and content to upload. (tuple)
    @return: None. (None)
    """
    object_key, content = data
    md5 = hashlib.md5(content).digest()
    md5b64 = DP.get_b64(md5).decode('utf-8')
    try:
        self.s3client.put_object(
            Bucket=self.s3_bucket_name,
            Key=object_key,
            Body=content,
            ContentMD5=md5b64,
        )
    except (ClientError, BotoCoreError) as exce:
        self.logger.error('Failed to upload %s to S3', object_key)
        self.logger.error(exce)
        # Raise to propagate error to the main thread
        raise exce
