from channels.routing import ProtocolTypeRouter, URLRouter
from pnotifications import routes

from .utils.jwt_auth_middleware import JwtAuthMiddleware

application = ProtocolTypeRouter(
    {
        "websocket": JwtAuthMiddleware(URLRouter(routes.websocket_urlpatterns)),
    }
)
