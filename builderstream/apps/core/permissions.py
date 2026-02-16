"""Standard permission classes for multi-tenant access control."""
from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    """Allow access to any member of the organization."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_id = view.kwargs.get("organization_id") or getattr(
            request, "organization_id", None
        )
        if not org_id:
            return True  # Let object-level check handle it
        return request.user.memberships.filter(
            organization_id=org_id, is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "organization"):
            return True
        return request.user.memberships.filter(
            organization=obj.organization, is_active=True
        ).exists()


class IsOrganizationAdmin(BasePermission):
    """Allow access only to organization admins."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_id = view.kwargs.get("organization_id") or getattr(
            request, "organization_id", None
        )
        if not org_id:
            return True
        return request.user.memberships.filter(
            organization_id=org_id,
            is_active=True,
            role__in=["admin", "owner"],
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "organization"):
            return True
        return request.user.memberships.filter(
            organization=obj.organization,
            is_active=True,
            role__in=["admin", "owner"],
        ).exists()


class IsOrganizationOwner(BasePermission):
    """Allow access only to the organization owner."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_id = view.kwargs.get("organization_id") or getattr(
            request, "organization_id", None
        )
        if not org_id:
            return True
        return request.user.memberships.filter(
            organization_id=org_id,
            is_active=True,
            role="owner",
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "organization"):
            return True
        return request.user.memberships.filter(
            organization=obj.organization,
            is_active=True,
            role="owner",
        ).exists()


# ---------------------------------------------------------------------------
# Role hierarchy for organization-level RBAC
# ---------------------------------------------------------------------------

ROLE_HIERARCHY = {
    "owner": 7,
    "admin": 6,
    "project_manager": 5,
    "estimator": 4,
    "accountant": 3,
    "field_worker": 2,
    "read_only": 1,
}


def role_required(min_role):
    """Factory function returning a permission class requiring a minimum role.

    Usage:
        permission_classes = [IsAuthenticated, role_required('project_manager')]
        # Allows: owner, admin, project_manager
        # Denies: estimator, accountant, field_worker, read_only
    """
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False

            org = getattr(request, "organization", None)
            if not org:
                return False

            user_role = (
                request.user.memberships.filter(
                    organization=org, is_active=True
                )
                .values_list("role", flat=True)
                .first()
            )
            if not user_role:
                return False

            return ROLE_HIERARCHY.get(user_role, 0) >= min_level

    RolePermission.__name__ = f"RoleRequired_{min_role}"
    RolePermission.__qualname__ = f"RoleRequired_{min_role}"
    return RolePermission
