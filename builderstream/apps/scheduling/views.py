"""Scheduling views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Crew, ScheduleTask
from .serializers import CrewSerializer, ScheduleTaskSerializer


class CrewViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_active"]
    search_fields = ["name"]


class ScheduleTaskViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = ScheduleTask.objects.all()
    serializer_class = ScheduleTaskSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "crew"]
    search_fields = ["name"]
