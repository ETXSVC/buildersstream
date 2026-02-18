"""Payroll & Workforce Management views."""
import logging
from datetime import date as date_cls

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember

from .models import CertifiedPayrollReport, Employee, PayrollEntry, PayrollRun, PrevailingWageRate
from .serializers import (
    CertifiedPayrollReportCreateSerializer,
    CertifiedPayrollReportDetailSerializer,
    CertifiedPayrollReportListSerializer,
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
    EmployeeListSerializer,
    PayrollEntryCreateSerializer,
    PayrollEntrySerializer,
    PayrollRunCreateSerializer,
    PayrollRunDetailSerializer,
    PayrollRunListSerializer,
    PrevailingWageRateCreateSerializer,
    PrevailingWageRateSerializer,
    UpdateCertificationSerializer,
)
from .services import CertifiedPayrollService, PayrollCalculationService, WorkforceService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

class EmployeeViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("user", "organization")
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["trade", "employment_type", "is_active"]
    search_fields = ["first_name", "last_name", "email", "employee_id"]
    ordering_fields = ["last_name", "first_name", "hire_date", "created_at"]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        if self.action == "create":
            return EmployeeCreateSerializer
        return EmployeeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def update_certification(self, request, pk=None):
        """Add or update a certification on the employee record."""
        employee = self.get_object()
        ser = UpdateCertificationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        updated = WorkforceService.update_certification(
            employee,
            cert_name=d["cert_name"],
            cert_number=d.get("cert_number", ""),
            expiry=d["expiry"],
            issuing_body=d.get("issuing_body", ""),
        )
        return Response(EmployeeDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def terminate(self, request, pk=None):
        """Mark an employee as inactive with an optional termination date."""
        employee = self.get_object()
        termination_date = None
        termination_date_str = request.data.get("termination_date")
        if termination_date_str:
            try:
                termination_date = date_cls.fromisoformat(termination_date_str)
            except ValueError:
                return Response(
                    {"detail": "Invalid termination_date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        updated = WorkforceService.terminate_employee(employee, termination_date)
        return Response(EmployeeDetailSerializer(updated).data)


# ---------------------------------------------------------------------------
# PayrollRun
# ---------------------------------------------------------------------------

class PayrollRunViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = (
        PayrollRun.objects
        .select_related("approved_by", "organization")
        .prefetch_related("entries")
    )
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["status"]
    search_fields = ["notes"]
    ordering_fields = ["pay_period_end", "created_at"]
    ordering = ["-pay_period_end"]

    def get_serializer_class(self):
        if self.action == "list":
            return PayrollRunListSerializer
        if self.action == "create":
            return PayrollRunCreateSerializer
        return PayrollRunDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def calculate(self, request, pk=None):
        """Populate PayrollEntries from approved TimeEntry records for the pay period."""
        payroll_run = self.get_object()
        entries = PayrollCalculationService.calculate_from_time_entries(payroll_run)
        return Response({
            "entries_created": len(entries),
            "detail": f"Calculated {len(entries)} payroll entries.",
        })

    @action(detail=True, methods=["post"])
    def add_entry(self, request, pk=None):
        """Manually add or override a single payroll entry."""
        payroll_run = self.get_object()
        ser = PayrollEntryCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        employee = d["employee"]
        if str(employee.organization_id) != str(payroll_run.organization_id):
            return Response(
                {"detail": "Employee does not belong to this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        calc = PayrollCalculationService.calculate_entry(
            employee,
            regular_hours=d["regular_hours"],
            overtime_hours=d.get("overtime_hours", 0),
            double_time_hours=d.get("double_time_hours", 0),
        )
        entry, created = PayrollEntry.objects.update_or_create(
            payroll_run=payroll_run,
            employee=employee,
            defaults=calc,
        )
        PayrollCalculationService._update_run_totals(payroll_run)
        return Response(
            PayrollEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a DRAFT or PROCESSING payroll run."""
        payroll_run = self.get_object()
        try:
            updated = PayrollCalculationService.approve_run(payroll_run, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PayrollRunDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark an APPROVED payroll run as PAID."""
        payroll_run = self.get_object()
        try:
            updated = PayrollCalculationService.mark_paid(payroll_run)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PayrollRunDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        """Void a payroll run (cannot void PAID runs)."""
        payroll_run = self.get_object()
        try:
            updated = PayrollCalculationService.void_run(payroll_run)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PayrollRunDetailSerializer(updated).data)


# ---------------------------------------------------------------------------
# CertifiedPayrollReport
# ---------------------------------------------------------------------------

class CertifiedPayrollViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = CertifiedPayrollReport.objects.select_related(
        "project", "payroll_run", "organization"
    )
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["project", "status", "report_type"]
    ordering_fields = ["week_ending", "created_at"]
    ordering = ["-week_ending"]

    def get_serializer_class(self):
        if self.action == "list":
            return CertifiedPayrollReportListSerializer
        if self.action == "create":
            return CertifiedPayrollReportCreateSerializer
        return CertifiedPayrollReportDetailSerializer

    def create(self, request, *args, **kwargs):
        """Delegate creation to CertifiedPayrollService.generate_report()."""
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        report = CertifiedPayrollService.generate_report(
            payroll_run=d["payroll_run"],
            project=d["project"],
            report_type=d.get("report_type", "wh_347"),
        )
        return Response(
            CertifiedPayrollReportDetailSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a DRAFT certified payroll report."""
        report = self.get_object()
        try:
            updated = CertifiedPayrollService.submit_report(report)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CertifiedPayrollReportDetailSerializer(updated).data)


# ---------------------------------------------------------------------------
# PrevailingWageRate
# ---------------------------------------------------------------------------

class PrevailingWageRateViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = PrevailingWageRate.objects.select_related("project", "organization")
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["project", "trade"]
    ordering_fields = ["effective_date", "trade"]
    ordering = ["-effective_date"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PrevailingWageRateCreateSerializer
        return PrevailingWageRateSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())


# ---------------------------------------------------------------------------
# Compliance Dashboard
# ---------------------------------------------------------------------------

class ComplianceDashboardView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        """Return payroll compliance summary for the organization."""
        from apps.tenants.context import get_current_organization

        org = get_current_organization()
        if org is None:
            return Response(
                {"detail": "Organization context not resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expiring = WorkforceService.get_expiring_certifications(org, days_ahead=30)
        skills = WorkforceService.get_skills_inventory(org)

        open_reports = CertifiedPayrollReport.objects.filter(
            organization=org,
            status=CertifiedPayrollReport.ReportStatus.DRAFT,
        ).select_related("project", "payroll_run")

        total_issues = sum(len(r.compliance_issues or []) for r in open_reports)

        return Response({
            "expiring_certifications": expiring,
            "workforce_skills": skills,
            "open_report_count": open_reports.count(),
            "total_compliance_issues": total_issues,
            "open_reports": CertifiedPayrollReportListSerializer(open_reports, many=True).data,
        })
