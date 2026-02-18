"""Field Operations Hub views."""
import logging
from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember, role_required

from .models import DailyLog, DailyLogCrewEntry, ExpenseEntry, TimeEntry
from .serializers import (
    BulkApproveSerializer,
    ClockInSerializer,
    ClockOutSerializer,
    DailyLogCreateSerializer,
    DailyLogCrewEntrySerializer,
    DailyLogDetailSerializer,
    DailyLogListSerializer,
    ExpenseEntryCreateSerializer,
    ExpenseEntryDetailSerializer,
    ExpenseEntryListSerializer,
    TimeEntryCreateSerializer,
    TimeEntryDetailSerializer,
    TimeEntryListSerializer,
)
from .services import BulkApprovalService, DailyLogService, TimeClockService

logger = logging.getLogger(__name__)

FIELD_OPS_ROLE = "field_worker"  # minimum role to access field ops


class DailyLogViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Daily field log management."""

    queryset = DailyLog.objects.select_related(
        "project", "submitted_by", "approved_by"
    ).prefetch_related("crew_entries")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "log_date", "safety_incidents"]
    search_fields = ["work_performed", "issues_encountered", "project__name"]
    ordering_fields = ["log_date", "status", "created_at"]
    ordering = ["-log_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return DailyLogListSerializer
        if self.action == "create":
            return DailyLogCreateSerializer
        return DailyLogDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            submitted_by=self.request.user,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a draft log for approval."""
        log = self.get_object()
        try:
            log = DailyLogService.submit_log(log, user=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DailyLogDetailSerializer(log, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a submitted log (PM or above)."""
        log = self.get_object()
        try:
            log = DailyLogService.approve_log(log, approver=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DailyLogDetailSerializer(log, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="crew-entries")
    def add_crew_entry(self, request, pk=None):
        """Add a crew entry to a daily log."""
        log = self.get_object()
        serializer = DailyLogCrewEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = serializer.save(daily_log=log)
        return Response(
            DailyLogCrewEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="attach-photos")
    def attach_photos(self, request, pk=None):
        """Attach photo IDs to a daily log."""
        log = self.get_object()
        photo_ids = request.data.get("photo_ids", [])
        if not photo_ids:
            return Response(
                {"detail": "photo_ids list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        DailyLogService.attach_photos(log, photo_ids)
        return Response({"detail": f"{len(photo_ids)} photo(s) attached."})


class TimeEntryViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Time entry management with clock in/out and bulk approval."""

    queryset = TimeEntry.objects.select_related("user", "project", "cost_code", "approved_by")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["user", "project", "date", "entry_type", "status"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "notes", "project__name"]
    ordering_fields = ["date", "clock_in", "hours", "status", "created_at"]
    ordering = ["-date", "-clock_in"]

    def get_serializer_class(self):
        if self.action == "list":
            return TimeEntryListSerializer
        if self.action == "create":
            return TimeEntryCreateSerializer
        if self.action == "clock_in":
            return ClockInSerializer
        if self.action == "clock_out":
            return ClockOutSerializer
        if self.action in ("bulk_approve", "bulk_reject"):
            return BulkApproveSerializer
        return TimeEntryDetailSerializer

    def perform_create(self, serializer):
        """Create a manual time entry."""
        serializer.save(
            organization=self.request.organization,
            user=self.request.user,
            entry_type=TimeEntry.EntryType.MANUAL,
            created_by=self.request.user,
        )

    # ------------------------------------------------------------------
    # Clock in / out
    # ------------------------------------------------------------------

    @action(detail=False, methods=["post"], url_path="clock-in")
    def clock_in(self, request):
        """Clock in for a project."""
        serializer = ClockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.projects.models import Project

        project = get_object_or_404(
            Project,
            pk=serializer.validated_data["project"],
            organization=request.organization,
        )
        entry, created = TimeClockService.clock_in(
            user=request.user,
            project=project,
            organization=request.organization,
            gps_data=serializer.validated_data.get("gps_data"),
            notes=serializer.validated_data.get("notes", ""),
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(
            TimeEntryDetailSerializer(entry, context=self.get_serializer_context()).data,
            status=response_status,
        )

    @action(detail=True, methods=["post"], url_path="clock-out")
    def clock_out(self, request, pk=None):
        """Clock out of an active time entry."""
        entry = self.get_object()
        if entry.clock_out:
            return Response(
                {"detail": "Already clocked out."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ClockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = TimeClockService.clock_out(
            entry=entry,
            gps_data=serializer.validated_data.get("gps_data"),
        )
        return Response(TimeEntryDetailSerializer(entry, context=self.get_serializer_context()).data)

    # ------------------------------------------------------------------
    # Bulk approval
    # ------------------------------------------------------------------

    @action(detail=False, methods=["post"], url_path="bulk-approve")
    def bulk_approve(self, request):
        """Bulk approve or reject time entries."""
        serializer = BulkApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"]
        action_type = serializer.validated_data.get("action", "approve")

        if action_type == "approve":
            count = BulkApprovalService.bulk_approve_time_entries(ids, request.user, request.organization)
        else:
            count = BulkApprovalService.bulk_reject_time_entries(ids, request.user, request.organization)

        return Response({"detail": f"{count} time entr{'y' if count == 1 else 'ies'} {action_type}d."})


class ExpenseEntryViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Expense entry management."""

    queryset = ExpenseEntry.objects.select_related("user", "project", "cost_code", "approved_by")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["user", "project", "date", "category", "status"]
    search_fields = ["description", "user__email", "project__name"]
    ordering_fields = ["date", "amount", "status", "created_at"]
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ExpenseEntryListSerializer
        if self.action == "create":
            return ExpenseEntryCreateSerializer
        if self.action == "bulk_approve":
            return BulkApproveSerializer
        return ExpenseEntryDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            user=self.request.user,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a single expense entry."""
        expense = self.get_object()
        if expense.status not in (ExpenseEntry.Status.PENDING,):
            return Response(
                {"detail": f"Cannot approve an expense in status '{expense.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from django.utils import timezone as django_tz
        expense.status = ExpenseEntry.Status.APPROVED
        expense.approved_by = request.user
        expense.approved_at = django_tz.now()
        expense.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return Response(ExpenseEntryDetailSerializer(expense, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="receipt-upload-url")
    def receipt_upload_url(self, request, pk=None):
        """Generate a presigned S3 URL for receipt upload."""
        expense = self.get_object()
        try:
            import boto3
            from django.conf import settings as django_settings
            s3 = boto3.client(
                "s3",
                aws_access_key_id=django_settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=django_settings.AWS_SECRET_ACCESS_KEY,
                region_name=django_settings.AWS_S3_REGION_NAME,
            )
            file_key = f"receipts/{expense.organization_id}/{expense.pk}.jpg"
            url = s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": django_settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": file_key,
                    "ContentType": "image/jpeg",
                },
                ExpiresIn=300,
            )
            return Response({"upload_url": url, "file_key": file_key})
        except Exception:
            return Response(
                {"detail": "Receipt upload not available (S3 not configured)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @action(detail=False, methods=["post"], url_path="bulk-approve")
    def bulk_approve(self, request):
        """Bulk approve expenses."""
        serializer = BulkApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["ids"]
        count = BulkApprovalService.bulk_approve_expenses(ids, request.user, request.organization)
        return Response({"detail": f"{count} expense{'s' if count != 1 else ''} approved."})


class TimesheetSummaryView(APIView):
    """Aggregate time entries by user/project/week with overtime breakdowns."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        from datetime import timedelta

        params = request.query_params
        user_id = params.get("user")
        project_id = params.get("project")
        week_str = params.get("week_start")  # YYYY-MM-DD

        user = None
        project = None

        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id, memberships__organization=request.organization)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if project_id:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(pk=project_id, organization=request.organization)
            except Project.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        week_start = None
        week_end = None
        if week_str:
            try:
                from datetime import date as dt
                week_start = dt.fromisoformat(week_str)
                week_end = week_start + timedelta(days=6)
            except ValueError:
                return Response({"detail": "Invalid week_start date."}, status=status.HTTP_400_BAD_REQUEST)

        summary = BulkApprovalService.get_timesheet_summary(
            organization=request.organization,
            user=user,
            project=project,
            week_start=week_start,
            week_end=week_end,
        )
        return Response({"results": summary, "count": len(summary)})


class DailyLogCalendarView(APIView):
    """Return daily log existence/status per date for a project (calendar data)."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        project_id = request.query_params.get("project")
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        if not all([project_id, year, month]):
            return Response(
                {"detail": "project, year, and month query params are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({"detail": "year and month must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.projects.models import Project
        project = get_object_or_404(Project, pk=project_id, organization=request.organization)

        calendar = DailyLogService.get_calendar_data(
            project=project,
            organization=request.organization,
            year=year,
            month=month,
        )
        return Response({"year": year, "month": month, "project": str(project.pk), "days": calendar})
