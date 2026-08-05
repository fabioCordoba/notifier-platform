from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs


class ApiKeyOrTokenMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)

        api_key_val = params.get('api_key', [None])[0]
        app_user_id = params.get('user_id', [None])[0]

        if api_key_val:
            organization = await self._authenticate(api_key_val)
            scope['organization'] = organization
        else:
            scope['organization'] = None

        scope['app_user_id'] = app_user_id
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def _authenticate(self, raw_key):
        from apps.organizations.models import ApiKey
        api_key = ApiKey.authenticate(raw_key)
        return api_key.organization if api_key else None
