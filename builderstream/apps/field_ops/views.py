"""Field operations views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import DailyLog, Expense, TimeEntry
from .serializers import DailyLogSerializer, ExpenseSerializer, TimeEntrySerializer


class DailyLogViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = DailyLog.objects.all()
    serializer_class = DailyLogSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "date"]


class TimeEntryViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "user", "date", "entry_type", "is_approved"]


class ExpenseViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "user", "status", "category"]
