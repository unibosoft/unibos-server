"""
ASGI config for UNIBOS Backend project.
Exposes the ASGI callable for WebSocket support.
"""

import os
import django
from django.core.asgi import get_asgi_application

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

# Import after Django setup
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from apps.common.middleware import JWTAuthMiddleware
import apps.documents.routing

# Django ASGI application
django_asgi_app = get_asgi_application()

# WebSocket routing
websocket_urlpatterns = []
websocket_urlpatterns += apps.documents.routing.websocket_urlpatterns

# Import other app routings if their consumers exist
try:
    import apps.currencies.routing
    websocket_urlpatterns += apps.currencies.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import apps.recaria.routing
    websocket_urlpatterns += apps.recaria.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import apps.birlikteyiz.routing
    websocket_urlpatterns += apps.birlikteyiz.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import apps.web_ui.routing
    websocket_urlpatterns += apps.web_ui.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    # HTTP protocol
    "http": django_asgi_app,
    
    # WebSocket protocol
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})