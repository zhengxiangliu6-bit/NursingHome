from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    try:
        token = AccessToken(token_str)
        return User.objects.select_related(
            'role', 'staff_profile', 'staff_profile__assigned_building'
        ).get(id=token['user_id'])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """从WebSocket查询参数中提取JWT token进行认证。"""

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = dict(
            p.split('=', 1) for p in query_string.split('&') if '=' in p
        )
        token = params.get('token', '')
        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)
