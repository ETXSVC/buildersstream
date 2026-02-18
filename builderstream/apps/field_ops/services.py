"""Field Operations Hub services: time clock, daily logs, bulk approval."""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone as django_tz

logger = logging.getLogger(__name__)

# Overtime rules — configurable constants
DAILY_OVERTIME_THRESHOLD = Decimal("8.00")      # hours before daily OT kicks in
WEEKLY_OVERTIME_THRESHOLD = Decimal("40.00")    # weekly hours before OT
DAILY_DOUBLE_TIME_THRESHOLD = Decimal("12.00")  # hours before double-time (CA style)
OT_MULTIPLIER = Decimal("1.5")
DT_MULTIPLIER = Decimal("2.0")


class TimeClockService:
    """Handle clock in/out with GPS validation and overtime calculation."""

    @staticmethod
    def clock_in(user, project, organization, gps_data=None, notes=""):
        """Create a new TimeEntry in CLOCK mode and record clock-in timestamp.

        Returns the new TimeEntry instance.
        """
        from .models import TimeEntry

        # Prevent double clock-in for same user/project on same day
        today = django_tz.localdate()
        open_entry = TimeEntry.objects.filter(
            organization=organization,
            user=user,
            project=project,
            date=today,
            clock_out__isnull=True,
            entry_type=TimeEntry.EntryType.CLOCK,
        ).first()
        if open_entry:
            return open_entry, False  # already clocked in

        is_within_geofence = None
        if gps_data and project.geofence_center:
            is_within_geofence = TimeClockService._check_geofence(
                gps_data, project.geofence_center, project.geofence_radius_m
            )
        elif gps_data:
            is_within_geofence = None  # no geofence configured — no check needed

        entry = TimeEntry.objects.create(
            organization=organization,
            user=user,
            project=project,
            date=today,
            clock_in=django_tz.now(),
            entry_type=TimeEntry.EntryType.CLOCK,
            status=TimeEntry.Status.PENDING,
            gps_clock_in=gps_data,
            is_within_geofence=is_within_geofence,
            notes=notes,
        )
        return entry, True

    @staticmethod
    def clock_out(entry, gps_data=None):
        """Record clock-out on an open TimeEntry. Calculates hours and overtime.

        Returns the updated entry.
        """
        if entry.clock_out:
            return entry  # already clocked out

        now = django_tz.now()
        entry.clock_out = now
        entry.hours = entry.calculate_hours()

        if gps_data:
            entry.gps_clock_out = gps_data

        # Calculate overtime for this entry (daily rules)
        if entry.hours > DAILY_DOUBLE_TIME_THRESHOLD:
            entry.overtime_hours = entry.hours - DAILY_DOUBLE_TIME_THRESHOLD
        elif entry.hours > DAILY_OVERTIME_THRESHOLD:
            entry.overtime_hours = entry.hours - DAILY_OVERTIME_THRESHOLD
        else:
            entry.overtime_hours = Decimal("0.00")

        entry.save(update_fields=[
            "clock_out", "hours", "overtime_hours", "gps_clock_out", "updated_at"
        ])
        return entry

    @staticmethod
    def create_manual_entry(user, project, organization, entry_date, hours,
                            cost_code=None, notes="", created_by=None):
        """Create a manual time entry (no clock in/out timestamps)."""
        from .models import TimeEntry

        if hours <= 0:
            raise ValueError("Hours must be positive.")

        overtime_hours = Decimal("0.00")
        if hours > DAILY_OVERTIME_THRESHOLD:
            overtime_hours = hours - DAILY_OVERTIME_THRESHOLD

        return TimeEntry.objects.create(
            organization=organization,
            user=user,
            project=project,
            date=entry_date,
            hours=hours,
            overtime_hours=overtime_hours,
            entry_type=TimeEntry.EntryType.MANUAL,
            status=TimeEntry.Status.PENDING,
            cost_code=cost_code,
            notes=notes,
            created_by=created_by,
        )

    @staticmethod
    def calculate_weekly_overtime(user, organization, week_start):
        """Recalculate overtime for all entries in a given week.

        Returns a list of (entry, new_overtime_hours) tuples.
        """
        from .models import TimeEntry

        week_end = week_start + timedelta(days=6)
        entries = TimeEntry.objects.filter(
            organization=organization,
            user=user,
            date__range=[week_start, week_end],
            status=TimeEntry.Status.PENDING,
        ).order_by("date", "clock_in")

        running_total = Decimal("0.00")
        updated = []

        for entry in entries:
            if entry.hours <= 0:
                continue

            # How many of this entry's hours are still under the weekly threshold?
            remaining_threshold = max(WEEKLY_OVERTIME_THRESHOLD - running_total, Decimal("0.00"))

            if remaining_threshold <= 0:
                # All hours this week are overtime
                new_ot = entry.hours
            elif entry.hours > remaining_threshold:
                new_ot = entry.hours - remaining_threshold
            else:
                new_ot = Decimal("0.00")

            # Weekly OT takes precedence — use whichever is higher
            final_ot = max(entry.overtime_hours, new_ot)

            if final_ot != entry.overtime_hours:
                entry.overtime_hours = final_ot
                updated.append(entry)

            running_total += entry.hours

        if updated:
            from django.db.models import F
            for e in updated:
                TimeEntry.objects.filter(pk=e.pk).update(overtime_hours=e.overtime_hours)

        return updated

    @staticmethod
    def _check_geofence(gps_data, center, radius_m):
        """Simple Haversine-based geofence check. Returns True if within radius."""
        import math

        lat1 = math.radians(gps_data.get("lat", 0))
        lon1 = math.radians(gps_data.get("lng", 0))
        lat2 = math.radians(center.get("lat", 0))
        lon2 = math.radians(center.get("lng", 0))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance_m = 6371000 * c  # Earth radius in meters

        return distance_m <= radius_m


class DailyLogService:
    """Create/update daily logs, approval workflow, auto-populate helpers."""

    @staticmethod
    def get_or_create_log(project, log_date, user, organization):
        """Get existing draft log or create a new one for the project/date."""
        from .models import DailyLog

        log, created = DailyLog.objects.get_or_create(
            organization=organization,
            project=project,
            log_date=log_date,
            defaults={
                "submitted_by": user,
                "status": DailyLog.Status.DRAFT,
                "created_by": user,
            },
        )
        return log, created

    @staticmethod
    def submit_log(log, user):
        """Transition log from DRAFT to SUBMITTED."""
        from .models import DailyLog

        if log.status != DailyLog.Status.DRAFT:
            raise ValueError(f"Cannot submit a log in status '{log.status}'.")

        log.status = DailyLog.Status.SUBMITTED
        log.submitted_by = user
        log.save(update_fields=["status", "submitted_by", "updated_at"])
        return log

    @staticmethod
    def approve_log(log, approver):
        """Transition log from SUBMITTED to APPROVED."""
        from .models import DailyLog

        if log.status != DailyLog.Status.SUBMITTED:
            raise ValueError(f"Cannot approve a log in status '{log.status}'.")

        log.status = DailyLog.Status.APPROVED
        log.approved_by = approver
        log.approved_at = django_tz.now()
        log.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return log

    @staticmethod
    def get_calendar_data(project, organization, year, month):
        """Return a dict mapping log_date → {status, id} for calendar display."""
        from .models import DailyLog

        logs = DailyLog.objects.filter(
            organization=organization,
            project=project,
            log_date__year=year,
            log_date__month=month,
        ).values("log_date", "id", "status")

        return {
            str(entry["log_date"]): {"id": str(entry["id"]), "status": entry["status"]}
            for entry in logs
        }

    @staticmethod
    def attach_photos(log, photo_ids):
        """Attach Photo objects to a daily log."""
        from apps.documents.models import Photo

        photos = Photo.objects.filter(pk__in=photo_ids)
        log.attached_photos.add(*photos)
        return log


class BulkApprovalService:
    """Batch approve time entries and expenses."""

    @staticmethod
    def bulk_approve_time_entries(entry_ids, approver, organization):
        """Approve a list of TimeEntry IDs. Returns approved count."""
        from .models import TimeEntry

        entries = TimeEntry.objects.filter(
            pk__in=entry_ids,
            organization=organization,
            status=TimeEntry.Status.PENDING,
        )
        now = django_tz.now()
        count = entries.update(
            status=TimeEntry.Status.APPROVED,
            approved_by=approver,
            approved_at=now,
        )
        return count

    @staticmethod
    def bulk_reject_time_entries(entry_ids, approver, organization):
        """Reject a list of TimeEntry IDs. Returns rejected count."""
        from .models import TimeEntry

        entries = TimeEntry.objects.filter(
            pk__in=entry_ids,
            organization=organization,
            status=TimeEntry.Status.PENDING,
        )
        now = django_tz.now()
        count = entries.update(
            status=TimeEntry.Status.REJECTED,
            approved_by=approver,
            approved_at=now,
        )
        return count

    @staticmethod
    def bulk_approve_expenses(expense_ids, approver, organization):
        """Approve a list of ExpenseEntry IDs. Returns approved count."""
        from .models import ExpenseEntry

        expenses = ExpenseEntry.objects.filter(
            pk__in=expense_ids,
            organization=organization,
            status=ExpenseEntry.Status.PENDING,
        )
        now = django_tz.now()
        count = expenses.update(
            status=ExpenseEntry.Status.APPROVED,
            approved_by=approver,
            approved_at=now,
        )
        return count

    @staticmethod
    def get_timesheet_summary(organization, user=None, project=None,
                              week_start=None, week_end=None):
        """Aggregate time entries by user/project/week with overtime breakdowns.

        Returns a list of dicts: {user_id, user_name, project_id, project_name,
        week_start, total_hours, overtime_hours, regular_hours, entry_count}
        """
        from .models import TimeEntry

        qs = TimeEntry.objects.filter(organization=organization)
        if user:
            qs = qs.filter(user=user)
        if project:
            qs = qs.filter(project=project)
        if week_start:
            qs = qs.filter(date__gte=week_start)
        if week_end:
            qs = qs.filter(date__lte=week_end)

        aggregated = (
            qs.values("user__id", "user__first_name", "user__last_name", "project__id", "project__name")
            .annotate(
                total_hours=Sum("hours"),
                overtime_hours=Sum("overtime_hours"),
                entry_count=Sum("id", distinct=True),
            )
            .order_by("user__last_name", "project__name")
        )

        results = []
        for row in aggregated:
            total = row["total_hours"] or Decimal("0.00")
            ot = row["overtime_hours"] or Decimal("0.00")
            results.append({
                "user_id": str(row["user__id"]),
                "user_name": f"{row['user__first_name']} {row['user__last_name']}".strip(),
                "project_id": str(row["project__id"]),
                "project_name": row["project__name"],
                "total_hours": float(total),
                "overtime_hours": float(ot),
                "regular_hours": float(total - ot),
                "week_start": str(week_start) if week_start else None,
            })
        return results
