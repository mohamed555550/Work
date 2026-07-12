from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


@database_sync_to_async
def _user_for_token(raw_token):
    authentication = JWTAuthentication()
    try:
        validated_token = authentication.get_validated_token(raw_token)
        return authentication.get_user(validated_token)
    except Exception:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get('query_string', b'').decode())
        tokens = query.get('token', [])
        subprotocols = scope.get('subprotocols', [])
        if len(subprotocols) >= 2 and subprotocols[0] == 'access_token':
            tokens = [subprotocols[1]]
        scope['user'] = await _user_for_token(tokens[0]) if tokens else AnonymousUser()
        return await super().__call__(scope, receive, send)
