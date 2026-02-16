"""Payroll views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin

from .models import CertifiedPayroll, PayPeriod, PayrollRecord
from .serializers import CertifiedPayrollSerializer, PayPeriodSerializer, PayrollRecordSerializer


class PayPeriodViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = PayPeriod.objects.all()
    serializer_class = PayPeriodSerializer
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["is_processed"]


class PayrollRecordViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = PayrollRecord.objects.all()
    serializer_class = PayrollRecordSerializer
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["pay_period", "employee"]


class CertifiedPayrollViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = CertifiedPayroll.objects.all()
    serializer_class = CertifiedPayrollSerializer
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["project", "is_submitted"]
