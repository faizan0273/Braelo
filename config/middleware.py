from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


class JWTAuthMiddleware(BaseMiddleware):
    '''
    Middleware for authenticating WebSocket connections using JWT tokens.
    If the token is invalid or missing, the connection is denied.
    '''

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_params = parse_qs(scope.get('query_string', b'').decode())
        token = query_params.get('token', [None])[0]

        if token:
            try:
                # Validate the token
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                if not user_id:
                    raise ValueError("Token is missing 'user_id' claim.")
                # Fetch the user from the database
                scope['user'] = await sync_to_async(User.objects.get)(
                    id=user_id
                )
            except (ValueError, User.DoesNotExist) as e:
                raise DenyConnection('Invalid or expired token.')
            except Exception as e:
                raise DenyConnection("Invalid or expired token.")
        else:
            raise DenyConnection('Authentication token required.')
        return await super().__call__(scope, receive, send)
