"""Tenant middleware for multi-tenant request isolation."""
from django.http import JsonResponse

from .context import clear_current_organization, set_current_organization
from .models import Organization, OrganizationMembership


class TenantMiddleware:
    """Resolve and enforce tenant context on every request.

    For authenticated users:
    1. Read 'X-Organization-ID' header (or fall back to user's active_organization)
    2. Validate the user has an active membership in that organization
    3. Store organization in thread-local AND request.organization
    4. Return 403 if no valid organization can be resolved
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        clear_current_organization()

        if request.user and request.user.is_authenticated:
            org = self._resolve_organization(request)

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

    def _resolve_organization(self, request):
        """Resolve organization from header or user default."""
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

        # 2. Fall back to user's active organization
        if hasattr(user, "active_organization") and user.active_organization_id:
            org = user.active_organization
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
            "/api/v1/accounts/register/",
            "/api/v1/accounts/token/",
            "/api/docs/",
            "/api/v1/tenants/organizations/",
        ]
        return any(path.startswith(prefix) for prefix in exempt_prefixes)
