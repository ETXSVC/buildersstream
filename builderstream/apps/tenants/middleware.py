"""Tenant middleware for multi-tenant request isolation."""
from django.http import JsonResponse

from .context import clear_current_organization, set_current_organization
from .models import Organization, OrganizationMembership


class TenantMiddleware:
    """Resolve and enforce tenant context on every request.

    For authenticated users:
    1. Read 'X-Organization-ID' header (or fall back to user's last_active_organization)
    2. Validate the user has an active membership in that organization
    3. Store organization in thread-local AND request.organization
    4. Return 403 if no valid organization can be resolved

    Note: Django's AuthenticationMiddleware resolves session-based users.
    For JWT-authenticated API requests, we must attempt JWT auth here because
    DRF only resolves request.user inside the view, after middleware has run.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        clear_current_organization()

        # Get the authenticated user — try session first, then JWT Bearer token
        user = request.user if (request.user and request.user.is_authenticated) else None
        if user is None:
            user = self._try_jwt_auth(request)

        if user and user.is_authenticated:
            org = self._resolve_organization(request, user)

            if org is None:
                # Allow admin and auth endpoints without org context
                if self._is_exempt_path(request.path):
                    response = self.get_response(request)
                    clear_current_organization()
                    return response

                return JsonResponse(
                    {"detail": "No valid organization found. Please join or create an organization."},
                    status=403,
                )

            request.organization = org
            set_current_organization(org)

        response = self.get_response(request)
        clear_current_organization()
        return response

    def _try_jwt_auth(self, request):
        """Attempt JWT authentication for Bearer-token API requests.

        Django middleware runs before DRF view authentication, so request.user
        is AnonymousUser for JWT clients. We authenticate here so TenantMiddleware
        can resolve the org context before the view executes.
        """
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            result = JWTAuthentication().authenticate(request)
            if result:
                return result[0]  # (user, validated_token)
        except Exception:
            pass
        return None

    def _resolve_organization(self, request, user=None):
        """Resolve organization from header or user default."""
        if user is None:
            user = request.user

        # 1. Check X-Organization-ID header
        org_id = request.headers.get("X-Organization-ID")
        if org_id:
            try:
                org = Organization.objects.get(id=org_id, is_active=True)
            except (Organization.DoesNotExist, ValueError):
                return None

            # Validate membership
            if OrganizationMembership.objects.filter(
                user=user, organization=org, is_active=True
            ).exists():
                return org
            return None

        # 2. Fall back to user's last active organization
        if hasattr(user, "last_active_organization") and user.last_active_organization_id:
            org = user.last_active_organization
            if org and org.is_active and OrganizationMembership.objects.filter(
                user=user, organization=org, is_active=True
            ).exists():
                return org

        # 3. Fall back to first active membership
        membership = (
            OrganizationMembership.objects.filter(user=user, is_active=True)
            .select_related("organization")
            .first()
        )
        if membership and membership.organization.is_active:
            return membership.organization

        return None

    def _is_exempt_path(self, path):
        """Paths that don't require organization context."""
        exempt_prefixes = [
            "/admin/",
            "/api/v1/auth/",
            "/api/v1/users/",
            "/api/v1/webhooks/",
            "/api/v1/billing/plans/",
            "/api/docs/",
            "/api/v1/tenants/organizations/",
        ]
        return any(path.startswith(prefix) for prefix in exempt_prefixes)
