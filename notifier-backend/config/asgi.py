import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

from apps.websocket.middleware import ApiKeyOrTokenMiddleware
import apps.websocket.routing as ws_routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        ApiKeyOrTokenMiddleware(
            URLRouter(ws_routing.websocket_urlpatterns)
        )
    ),
})
