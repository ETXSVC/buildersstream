"""WebSocket URL routing for collaboration app."""
from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/collaboration/channels/(?P<channel_id>[^/]+)/$",
        ChatConsumer.as_asgi(),
    ),
]
