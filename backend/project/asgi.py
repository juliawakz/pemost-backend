import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from pnotifications import routes

from .utils.token_auth_middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                routes.websocket_urlpatterns
            )
        )
    )
})
