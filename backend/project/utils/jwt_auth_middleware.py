from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# from rest_framework_simplejwt.state import
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user = User.objects.get(id=validated_token["user_id"])
        return user

    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()
        # Get the token
        header = dict(scope["headers"])
        # Initialising empty dictionary
        headers = {}
        # Converting
        for key, value in header.items():
            headers[key.decode("utf-8")] = value.decode("utf-8")
        if "sec-websocket-protocol" in headers:
            token = headers.get("sec-websocket-protocol")
            # Try to authenticate the user
            try:
                # This will automatically validate the token and raise an error if token is invalid
                UntypedToken(token)
            except (InvalidToken, TokenError):
                # Token is invalid
                scope["user"] = AnonymousUser()
                return await super().__call__(scope, receive, send)
                # return None
            else:
                #  Then token is valid, decode it
                decoded_data = jwt_decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                # Get the user using ID
                scope["user"] = await get_user(validated_token=decoded_data)
            return await super().__call__(scope, receive, send)

        else:
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
