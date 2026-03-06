"""
Cookie-based JWT authentication.

DRF backend: reads access token from HttpOnly cookie 'bs_access'.
Channels middleware: reads access token from cookie header in WS scope.
"""
from http.cookies import SimpleCookie

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

COOKIE_NAME = "bs_access"


# ---------------------------------------------------------------------------
# DRF authentication class
# ---------------------------------------------------------------------------

class JWTCookieAuthentication(JWTAuthentication):
    """Read JWT access token from HttpOnly cookie instead of Authorization header."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(COOKIE_NAME)
        if not raw_token:
            # Fall back to header-based auth (keeps Swagger / curl working)
            return super().authenticate(request)
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None


# ---------------------------------------------------------------------------
# Django Channels ASGI middleware
# ---------------------------------------------------------------------------

class JWTCookieAuthMiddleware:
    """
    Channels middleware that authenticates WebSocket connections via the
    'bs_access' HttpOnly cookie.  Sets scope['user'] so consumers can use
    self.scope['user'] instead of parsing query-string tokens.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("websocket", "http"):
            scope["user"] = await self._get_user(scope)
        return await self.inner(scope, receive, send)

    async def _get_user(self, scope):
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode("latin-1")

        cookie = SimpleCookie()
        cookie.load(cookie_header)

        morsel = cookie.get(COOKIE_NAME)
        if not morsel:
            return AnonymousUser()

        try:
            token = AccessToken(morsel.value)
            user_id = token["user_id"]
            from apps.accounts.models import User  # noqa: PLC0415
            return await database_sync_to_async(User.objects.get)(pk=user_id)
        except (TokenError, Exception):
            return AnonymousUser()
