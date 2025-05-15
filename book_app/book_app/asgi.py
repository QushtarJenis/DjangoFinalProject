# book_app/asgi.py
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_app.settings')
django.setup()

# Import after Django setup
from friends.middleware import JWTAuthMiddleware
from friends.routing import websocket_urlpatterns
import logging

# Set up logger
logger = logging.getLogger("channels")

# Log the websocket_urlpatterns for debugging
for pattern in websocket_urlpatterns:
    logger.info(f"Registered WebSocket route: {pattern.pattern}")

# Set up Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})