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
