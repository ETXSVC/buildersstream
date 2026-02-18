"""Quality & Safety services."""
import calendar
import logging
from datetime import date

from django.db import transaction

logger = logging.getLogger(__name__)


class InspectionService:
    """Inspection lifecycle and scoring logic."""

    @staticmethod
    def create_from_checklist(checklist, project, organization, inspector=None, inspection_date=None):
        """Create a new Inspection from a checklist, seeding empty InspectionResults."""
        from .models import Inspection, InspectionResult

        if inspection_date is None:
            inspection_date = date.today()

        with transaction.atomic():
            inspection = Inspection.objects.create(
                organization=organization,
                project=project,
                checklist=checklist,
                inspector=inspector,
                inspection_date=inspection_date,
                status=Inspection.Status.SCHEDULED,
            )
            items = list(checklist.items.order_by("sort_order"))
            InspectionResult.objects.bulk_create([
                InspectionResult(
                    inspection=inspection,
                    checklist_item=item,
                    status=InspectionResult.Status.NOT_INSPECTED,
                )
                for item in items
            ])
        return inspection

    @staticmethod
    def calculate_score(inspection):
        """Calculate 0-100 quality score.

        Score = PASS / (PASS + FAIL) * 100, ignoring NA and NOT_INSPECTED.
        Returns None if no inspectable items.
        """
        from .models import InspectionResult

        results = list(inspection.results.all())
        inspectable = [
            r for r in results
            if r.status not in (InspectionResult.Status.NA, InspectionResult.Status.NOT_INSPECTED)
        ]
        if not inspectable:
            return None
        passed = sum(1 for r in inspectable if r.status == InspectionResult.Status.PASS)
        return round((passed / len(inspectable)) * 100)

    @staticmethod
    def record_results(inspection, results_data):
        """Bulk update inspection results and recalculate score.

        results_data: list of {checklist_item_id, status, notes, photo_id (optional)}
        """
        from .models import InspectionResult

        updates = []
        for data in results_data:
            try:
                result = InspectionResult.objects.get(
                    inspection=inspection,
                    checklist_item_id=data["checklist_item_id"],
                )
                result.status = data.get("status", result.status)
                result.notes = data.get("notes", result.notes)
                if data.get("photo_id"):
                    result.photo_id = data["photo_id"]
                updates.append(result)
            except InspectionResult.DoesNotExist:
                logger.warning(
                    "InspectionResult not found for item %s in inspection %s",
                    data.get("checklist_item_id"), inspection.pk,
                )

        if updates:
            InspectionResult.objects.bulk_update(updates, ["status", "notes", "photo_id"])

        score = InspectionService.calculate_score(inspection)
        inspection.overall_score = score
        if inspection.status == inspection.Status.SCHEDULED:
            inspection.status = inspection.Status.IN_PROGRESS
        inspection.save(update_fields=["overall_score", "status", "updated_at"])
        return inspection

    @staticmethod
    def complete_inspection(inspection, final_status, overall_score=None, notes=""):
        """Set the final status (PASSED/FAILED/CONDITIONAL) and optional score."""
        from .models import Inspection

        allowed = (Inspection.Status.PASSED, Inspection.Status.FAILED, Inspection.Status.CONDITIONAL)
        if final_status not in allowed:
            raise ValueError(f"Final status must be one of {allowed}.")
        if inspection.status in (Inspection.Status.PASSED, Inspection.Status.FAILED):
            raise ValueError(f"Inspection already finalized with status '{inspection.status}'.")

        if overall_score is None:
            overall_score = InspectionService.calculate_score(inspection)
        if notes:
            inspection.notes = notes
        inspection.status = final_status
        inspection.overall_score = overall_score
        inspection.save(update_fields=["status", "overall_score", "notes", "updated_at"])
        return inspection

    @staticmethod
    def generate_report(inspection):
        """Return dict summary of inspection results (no PDF — data only)."""
        results = inspection.results.select_related("checklist_item").all()

        by_status = {}
        failed_required = 0
        for r in results:
            key = r.status
            by_status.setdefault(key, []).append({
                "item": r.checklist_item.description,
                "required": r.checklist_item.is_required,
                "notes": r.notes,
                "photo_id": str(r.photo_id) if r.photo_id else None,
            })
            if r.status == "fail" and r.checklist_item.is_required:
                failed_required += 1

        return {
            "inspection_id": str(inspection.pk),
            "checklist": inspection.checklist.name,
            "checklist_type": inspection.checklist.checklist_type,
            "category": inspection.checklist.category,
            "project_id": str(inspection.project_id),
            "inspector_id": str(inspection.inspector_id) if inspection.inspector_id else None,
            "inspection_date": str(inspection.inspection_date),
            "status": inspection.status,
            "overall_score": inspection.overall_score,
            "results_by_status": by_status,
            "total_items": results.count(),
            "failed_required_items": failed_required,
        }


class DeficiencyService:
    """Deficiency lifecycle management."""

    @staticmethod
    def resolve(deficiency, notes, resolved_by):
        """Transition OPEN or IN_PROGRESS → RESOLVED."""
        from .models import Deficiency

        if deficiency.status not in (Deficiency.Status.OPEN, Deficiency.Status.IN_PROGRESS):
            raise ValueError(
                f"Cannot resolve a deficiency with status '{deficiency.status}'. "
                "Must be OPEN or IN_PROGRESS."
            )
        deficiency.status = Deficiency.Status.RESOLVED
        deficiency.resolution_notes = notes
        deficiency.resolved_by = resolved_by
        deficiency.resolved_date = date.today()
        deficiency.save(
            update_fields=["status", "resolution_notes", "resolved_by", "resolved_date", "updated_at"]
        )
        return deficiency

    @staticmethod
    def verify(deficiency, verifier):
        """Transition RESOLVED → VERIFIED."""
        from .models import Deficiency

        if deficiency.status != Deficiency.Status.RESOLVED:
            raise ValueError("Can only verify a deficiency that has been resolved.")
        deficiency.status = Deficiency.Status.VERIFIED
        deficiency.verified_by = verifier
        deficiency.save(update_fields=["status", "verified_by", "updated_at"])
        return deficiency

    @staticmethod
    def reopen(deficiency, user, notes=""):
        """Reopen a RESOLVED deficiency back to IN_PROGRESS."""
        from .models import Deficiency

        if deficiency.status not in (Deficiency.Status.RESOLVED, Deficiency.Status.VERIFIED):
            raise ValueError("Can only reopen a resolved or verified deficiency.")
        deficiency.status = Deficiency.Status.IN_PROGRESS
        if notes:
            deficiency.resolution_notes = (
                f"REOPENED: {notes}\n\n---\n\n" + deficiency.resolution_notes
            )
        deficiency.resolved_date = None
        deficiency.save(update_fields=["status", "resolution_notes", "resolved_date", "updated_at"])
        return deficiency


class SafetyService:
    """Safety incident workflow."""

    @staticmethod
    def advance_status(incident, new_status):
        """Advance incident to a new status (enforces forward-only progression)."""
        from .models import SafetyIncident

        status_order = [
            SafetyIncident.IncidentStatus.REPORTED,
            SafetyIncident.IncidentStatus.INVESTIGATING,
            SafetyIncident.IncidentStatus.CORRECTIVE_ACTION,
            SafetyIncident.IncidentStatus.CLOSED,
        ]
        current_idx = status_order.index(incident.status)
        new_idx = status_order.index(new_status)
        if new_idx <= current_idx:
            raise ValueError(
                f"Cannot transition incident from '{incident.status}' to '{new_status}'."
            )
        incident.status = new_status
        incident.save(update_fields=["status", "updated_at"])
        return incident

    @staticmethod
    def close_incident(incident, corrective_notes=""):
        """Close an incident, optionally appending corrective action notes."""
        from .models import SafetyIncident

        if incident.status == SafetyIncident.IncidentStatus.CLOSED:
            raise ValueError("Incident is already closed.")
        if corrective_notes:
            sep = "\n\n" if incident.corrective_actions else ""
            incident.corrective_actions = incident.corrective_actions + sep + corrective_notes
        incident.status = SafetyIncident.IncidentStatus.CLOSED
        incident.save(update_fields=["status", "corrective_actions", "updated_at"])
        return incident


class QualityAnalyticsService:
    """Analytics queries for quality and safety data."""

    @staticmethod
    def get_quality_scores(project, organization):
        """Return [{date, score, status, checklist}] for a project's inspections."""
        from .models import Inspection

        inspections = (
            Inspection.objects.filter(
                organization=organization,
                project=project,
                overall_score__isnull=False,
            )
            .order_by("inspection_date")
            .select_related("checklist")
        )
        return [
            {
                "date": str(i.inspection_date),
                "score": i.overall_score,
                "status": i.status,
                "checklist": i.checklist.name,
                "category": i.checklist.category,
            }
            for i in inspections
        ]

    @staticmethod
    def get_incident_trends(organization, months=6):
        """Return monthly incident counts for the past N months."""
        from .models import SafetyIncident

        today = date.today()
        results = []

        for i in range(months - 1, -1, -1):
            # Compute year/month N months ago
            raw_month = today.month - i
            year = today.year + (raw_month - 1) // 12
            month = ((raw_month - 1) % 12) + 1
            _, last_day = calendar.monthrange(year, month)
            month_start = date(year, month, 1)
            month_end = date(year, month, last_day)

            qs = SafetyIncident.objects.filter(
                organization=organization,
                incident_date__date__gte=month_start,
                incident_date__date__lte=month_end,
            )
            results.append({
                "month": f"{year:04d}-{month:02d}",
                "total": qs.count(),
                "osha_reportable": qs.filter(osha_reportable=True).count(),
                "by_severity": {
                    sev: qs.filter(severity=sev).count()
                    for sev in ("first_aid", "medical", "lost_time", "fatality")
                },
            })
        return results

    @staticmethod
    def get_deficiency_stats(organization, project=None):
        """Return deficiency counts by status and severity."""
        from django.db.models import Count

        from .models import Deficiency

        qs = Deficiency.objects.filter(organization=organization)
        if project:
            qs = qs.filter(project=project)

        by_status = dict(
            qs.values_list("status").annotate(c=Count("id")).values_list("status", "c")
        )
        by_severity = dict(
            qs.values_list("severity").annotate(c=Count("id")).values_list("severity", "c")
        )
        return {
            "by_status": by_status,
            "by_severity": by_severity,
            "total_open": by_status.get("open", 0) + by_status.get("in_progress", 0),
            "total_resolved": by_status.get("resolved", 0) + by_status.get("verified", 0),
        }

    @staticmethod
    def get_safety_summary(organization, project=None):
        """Return overall safety summary for an org/project."""
        from .models import SafetyIncident, ToolboxTalk

        qs_incident = SafetyIncident.objects.filter(organization=organization)
        qs_tbt = ToolboxTalk.objects.filter(organization=organization)
        if project:
            qs_incident = qs_incident.filter(project=project)
            qs_tbt = qs_tbt.filter(project=project)

        year_start = date.today().replace(month=1, day=1)
        return {
            "incidents_ytd": qs_incident.filter(incident_date__date__gte=year_start).count(),
            "osha_reportable_ytd": qs_incident.filter(
                incident_date__date__gte=year_start, osha_reportable=True
            ).count(),
            "open_incidents": qs_incident.exclude(status="closed").count(),
            "toolbox_talks_ytd": qs_tbt.filter(presented_date__gte=year_start).count(),
        }
