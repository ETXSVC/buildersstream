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


class HasModuleAccess(BasePermission):
    """Permission class that checks if a module is active for the organization."""

    def __init__(self, module_key):
        """Initialize with the module key to check."""
        self.module_key = module_key
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user's organization has the module active."""
        if not request.user or not request.user.is_authenticated:
            return False

        org = getattr(request, "organization", None)
        if not org:
            return False

        # Check if module is active for this organization
        from apps.tenants.models import ActiveModule

        # Always-active modules - compare string values
        always_active_keys = {mod.value for mod in ActiveModule.ALWAYS_ACTIVE}
        if self.module_key in always_active_keys:
            return True

        # Check if module is explicitly activated
        return ActiveModule.objects.filter(
            organization=org,
            module_key=self.module_key,
            is_active=True,
        ).exists()


def has_module_access(module_key):
    """Factory function returning a permission class for module access.

    Usage:
        permission_classes = [IsOrganizationMember, has_module_access('CRM')]
    """

    class ModuleAccessPermission(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False

            org = getattr(request, "organization", None)
            if not org:
                return False

            # Check if module is active for this organization
            from apps.tenants.models import ActiveModule

            # Always-active modules - compare string values
            always_active_keys = {mod.value for mod in ActiveModule.ALWAYS_ACTIVE}
            if module_key in always_active_keys:
                return True

            # Check if module is explicitly activated
            return ActiveModule.objects.filter(
                organization=org,
                module_key=module_key,
                is_active=True,
            ).exists()

    ModuleAccessPermission.__name__ = f"HasModuleAccess_{module_key}"
    ModuleAccessPermission.__qualname__ = f"HasModuleAccess_{module_key}"
    return ModuleAccessPermission


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
