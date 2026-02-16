"""ViewSet mixins for multi-tenant functionality."""


class TenantViewSetMixin:
    """Mixin that auto-injects organization filtering into viewsets.

    - Filters querysets by the user's active organization.
    - Injects organization into serializer context.
    - Auto-sets organization and created_by on object creation.
    """

    def get_organization(self):
        """Resolve the current organization from request context."""
        org_id = self.kwargs.get("organization_id")
        if org_id:
            return org_id
        # Fall back to user's active organization
        user = self.request.user
        if hasattr(user, "last_active_organization"):
            return user.last_active_organization_id
        membership = user.memberships.filter(is_active=True).first()
        return membership.organization_id if membership else None

    def get_queryset(self):
        """Filter queryset by the user's organization."""
        qs = super().get_queryset()
        org_id = self.get_organization()
        if org_id and hasattr(qs.model, "organization"):
            qs = qs.filter(organization_id=org_id)
        return qs

    def get_serializer_context(self):
        """Add organization to serializer context."""
        context = super().get_serializer_context()
        context["organization_id"] = self.get_organization()
        return context

    def perform_create(self, serializer):
        """Auto-set organization and created_by on creation."""
        kwargs = {}
        org_id = self.get_organization()
        if org_id:
            kwargs["organization_id"] = org_id
        if hasattr(serializer.Meta.model, "created_by"):
            kwargs["created_by"] = self.request.user
        serializer.save(**kwargs)
