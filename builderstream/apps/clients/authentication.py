"""
Client Portal JWT Authentication.

Separate from contractor JWT auth — these tokens are:
  - Scoped to a specific ClientPortalAccess record
  - Short-lived (8 hours by default)
  - NOT usable for internal/contractor API endpoints
  - Carry {portal_access_id, contact_id, project_id, organization_id}
"""

import logging
from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

# Portal JWT settings (can override in settings.py)
PORTAL_TOKEN_LIFETIME = getattr(settings, "PORTAL_TOKEN_LIFETIME_HOURS", 8)
PORTAL_JWT_ALGORITHM = "HS256"
PORTAL_JWT_CLAIM = "portal_access"  # Distinguishes portal tokens from contractor tokens


def generate_portal_token(portal_access) -> str:
    """
    Generate a short-lived JWT scoped to a specific ClientPortalAccess record.

    Payload:
        type: "portal" — marker to distinguish from contractor JWTs
        portal_access_id: UUID of the ClientPortalAccess
        contact_id: UUID of the CRM Contact
        project_id: UUID of the Project
        organization_id: UUID of the Organization
        exp: expiry timestamp
        iat: issued-at timestamp
    """
    now = timezone.now()
    payload = {
        "type": PORTAL_JWT_CLAIM,
        "portal_access_id": str(portal_access.pk),
        "contact_id": str(portal_access.contact_id),
        "project_id": str(portal_access.project_id),
        "organization_id": str(portal_access.organization_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=PORTAL_TOKEN_LIFETIME)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=PORTAL_JWT_ALGORITHM)


def decode_portal_token(token: str) -> dict:
    """
    Decode and validate a portal JWT.

    Raises:
        AuthenticationFailed if token is invalid, expired, or not a portal token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[PORTAL_JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Portal session has expired. Please use a new magic link.")
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed(f"Invalid portal token: {exc}")

    if payload.get("type") != PORTAL_JWT_CLAIM:
        raise AuthenticationFailed("Token is not a portal token.")

    return payload


class PortalAccessUser:
    """
    Lightweight user-like object for portal requests.

    Attached to request.user for client portal views.
    request.portal_access = ClientPortalAccess instance
    request.portal_contact = CRM Contact instance
    """

    def __init__(self, portal_access):
        self.portal_access = portal_access
        self.contact = portal_access.contact
        self.project = portal_access.project
        self.organization = portal_access.organization
        self.is_authenticated = True
        self.is_portal_user = True
        # Standard Django checks
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False
        self.pk = str(portal_access.pk)

    def has_permission(self, perm_key: str) -> bool:
        """Check a granular portal permission."""
        return self.portal_access.permissions.get(perm_key, False)

    def __str__(self):
        return f"PortalUser({self.contact})"


class ClientPortalAuthentication(BaseAuthentication):
    """
    DRF authentication backend for client portal tokens.

    Checks the Authorization header for 'Portal <token>' scheme.
    On success, attaches a PortalAccessUser to request.user and sets
    request.organization for TenantMiddleware compatibility.
    """

    keyword = "Portal"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # Not a portal token — let other backends try

        token = auth_header[len(f"{self.keyword} "):]

        try:
            payload = decode_portal_token(token)
        except AuthenticationFailed:
            raise

        from apps.clients.models import ClientPortalAccess

        portal_access_id = payload.get("portal_access_id")
        try:
            portal_access = (
                ClientPortalAccess.objects
                .select_related("contact", "project", "organization")
                .get(pk=portal_access_id, is_active=True)
            )
        except ClientPortalAccess.DoesNotExist:
            raise AuthenticationFailed("Portal access not found or deactivated.")

        # Inject organization into request for downstream middleware
        request.organization = portal_access.organization

        return (PortalAccessUser(portal_access), token)

    def authenticate_header(self, request):
        return self.keyword
