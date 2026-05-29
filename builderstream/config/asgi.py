"""ASGI config for BuilderStream project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Initialize Django ASGI application early to populate AppRegistry before
# importing channels consumers that reference models.
_base_asgi_app = get_asgi_application()

# Wrap with static files handler in development so Daphne serves /static/ files.
import django  # noqa: E402
from django.conf import settings  # noqa: E402

if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
    django_asgi_app = ASGIStaticFilesHandler(_base_asgi_app)
else:
    django_asgi_app = _base_asgi_app

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from apps.accounts.authentication import JWTCookieAuthMiddleware  # noqa: E402

import apps.notifications.routing  # noqa: E402
import apps.collaboration.routing  # noqa: E402

all_websocket_urlpatterns = (
    apps.notifications.routing.websocket_urlpatterns
    + apps.collaboration.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTCookieAuthMiddleware(
                URLRouter(all_websocket_urlpatterns)
            )
        ),
    }
)
