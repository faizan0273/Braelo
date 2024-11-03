'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
braelo decorators file.
---------------------------------------------------
'''

from functools import wraps
from rest_framework import status
from pymongo.errors import PyMongoError
from rest_framework.exceptions import ValidationError
from sqlite3 import OperationalError as SQLITE_ERROR
from helpers import get_error_details, response


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as err:
            error = get_error_details(err.detail)
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Validation Error',
                data=args[1].data,  # Request data
                error=error,
            )
        except SQLITE_ERROR as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Database failure',
                data=args[1].data,
                error=str(err),
            )
        except PyMongoError as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Mongo DB failure',
                data=args[1].data,
                error=str(err),
            )
        except Exception as err:
            return response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Exception',
                data=args[1].data,
                error=str(err),
            )

    return wrapper
