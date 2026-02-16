"""Project views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "project_type", "is_active"]
    search_fields = ["name", "number", "description"]
    ordering_fields = ["name", "created_at", "start_date", "contract_amount"]
