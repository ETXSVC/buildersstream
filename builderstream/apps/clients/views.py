"""Client portal views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import ClientPortalAccess, Selection
from .serializers import ClientPortalAccessSerializer, SelectionSerializer


class ClientPortalAccessViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = ClientPortalAccess.objects.all()
    serializer_class = ClientPortalAccessSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "is_active"]


class SelectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "category"]
