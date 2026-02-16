"""Tenant-level permission classes."""
from rest_framework.permissions import BasePermission

from .models import ActiveModule


class HasModuleAccess(BasePermission):
    """Check if the request's organization has a specific module active.

    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasModuleAccess('CRM')]
    """

    def __init__(self, module_key):
        self.module_key = module_key

    def has_permission(self, request, view):
        org = getattr(request, "organization", None)
        if org is None:
            return False
        return ActiveModule.objects.filter(
            organization=org,
            module_key=self.module_key,
            is_active=True,
        ).exists()

    def __call__(self):
        """Allow use as permission_classes = [HasModuleAccess('CRM')]."""
        return self
