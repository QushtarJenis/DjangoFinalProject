# friends/asgi.py
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from channels.auth import AuthMiddlewareStack
from .consumers import ChatConsumer  # Update with your actual consumer

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_app.settings')
django.setup()  # This is important!

# Django ASGI application
django_asgi_app = get_asgi_application()

# WebSocket routing
websocket_urlpatterns = [
    re_path(r'ws/friends/chat/(?P<friend_id>\\d+)/?$', ChatConsumer.as_asgi()),
]

# Combined ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})