"""Analytics & Reporting Engine services."""
import csv
import io
import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class KPIService:
    """Calculate and store KPIs from live source data across all modules."""

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    @staticmethod
    def calculate_all_kpis(organization):
        """Calculate and upsert standard KPIs for the current month."""
        today = timezone.now().date()
        period_start = today.replace(day=1)
        period_end = today

        results = []
        results += KPIService._financial_kpis(organization, period_start, period_end)
        results += KPIService._project_kpis(organization, period_start, period_end)
        results += KPIService._labor_kpis(organization, period_start, period_end)
        results += KPIService._safety_kpis(organization, period_start, period_end)
        results += KPIService._service_kpis(organization, period_start, period_end)
        return results

    @staticmethod
    def get_org_summary(organization):
        """Return a live summary dict with key metrics for the org dashboard."""
        today = timezone.now().date()
        period_start = today.replace(day=1)

        return {
            "financial": KPIService._financial_summary(organization, period_start, today),
            "projects": KPIService._project_summary(organization),
            "labor": KPIService._labor_summary(organization, period_start, today),
            "safety": KPIService._safety_summary(organization, period_start, today),
            "service": KPIService._service_summary(organization),
        }

    # ------------------------------------------------------------------ #
    # Financial
    # ------------------------------------------------------------------ #

    @staticmethod
    def _financial_summary(org, period_start, period_end):
        from apps.financials.models import Invoice, Expense, Budget

        revenue = (
            Invoice.objects.filter(
                organization=org,
                issue_date__gte=period_start,
                issue_date__lte=period_end,
                status__in=["sent", "paid", "partially_paid"],
            ).aggregate(total=Sum("total"))["total"] or Decimal("0")
        )

        expenses = (
            Expense.objects.filter(
                organization=org,
                expense_date__gte=period_start,
                expense_date__lte=period_end,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )

        overdue_count = Invoice.objects.filter(
            organization=org,
            due_date__lt=period_end,
            status__in=["sent", "overdue"],
        ).count()

        overdue_amount = (
            Invoice.objects.filter(
                organization=org,
                due_date__lt=period_end,
                status__in=["sent", "overdue"],
            ).aggregate(total=Sum("total"))["total"] or Decimal("0")
        )

        budget_variance = (
            Budget.objects.filter(organization=org)
            .aggregate(
                total_budgeted=Sum("budgeted_amount"),
                total_actual=Sum("actual_amount"),
            )
        )
        budgeted = budget_variance["total_budgeted"] or Decimal("0")
        actual = budget_variance["total_actual"] or Decimal("0")

        return {
            "revenue_mtd": float(revenue),
            "expenses_mtd": float(expenses),
            "gross_profit_mtd": float(revenue - expenses),
            "overdue_invoices_count": overdue_count,
            "overdue_invoices_amount": float(overdue_amount),
            "total_budgeted": float(budgeted),
            "total_actual_cost": float(actual),
            "budget_variance": float(budgeted - actual),
        }

    @staticmethod
    def _financial_kpis(org, period_start, period_end):
        summary = KPIService._financial_summary(org, period_start, period_end)
        kpis = [
            ("Revenue MTD", "financial", summary["revenue_mtd"], None, "USD"),
            ("Expenses MTD", "financial", summary["expenses_mtd"], None, "USD"),
            ("Gross Profit MTD", "financial", summary["gross_profit_mtd"], None, "USD"),
            ("Overdue Invoices", "financial", summary["overdue_invoices_count"], 0, "count"),
            ("Budget Variance", "financial", summary["budget_variance"], None, "USD"),
        ]
        return KPIService._upsert_kpis(org, kpis, period_start, period_end)

    # ------------------------------------------------------------------ #
    # Projects
    # ------------------------------------------------------------------ #

    @staticmethod
    def _project_summary(org):
        from apps.projects.models import Project

        status_counts = dict(
            Project.objects.filter(organization=org)
            .values_list("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        active = Project.objects.filter(
            organization=org,
            status__in=["production", "punch_list"],
        )
        total_active = active.count()

        # Health breakdown
        health_counts = dict(
            active.values_list("health_status")
            .annotate(count=Count("id"))
            .values_list("health_status", "count")
        )

        return {
            "total_projects": Project.objects.filter(organization=org).count(),
            "active_projects": total_active,
            "status_breakdown": status_counts,
            "health_green": health_counts.get("green", 0),
            "health_yellow": health_counts.get("yellow", 0),
            "health_red": health_counts.get("red", 0),
        }

    @staticmethod
    def _project_kpis(org, period_start, period_end):
        summary = KPIService._project_summary(org)
        kpis = [
            ("Active Projects", "project", summary["active_projects"], None, "count"),
            ("Projects Health Green", "project", summary["health_green"], None, "count"),
            ("Projects Health Red", "project", summary["health_red"], 0, "count"),
        ]
        return KPIService._upsert_kpis(org, kpis, period_start, period_end)

    # ------------------------------------------------------------------ #
    # Labor
    # ------------------------------------------------------------------ #

    @staticmethod
    def _labor_summary(org, period_start, period_end):
        from apps.field_ops.models import TimeEntry

        approved = TimeEntry.objects.filter(
            organization=org,
            clock_in__date__gte=period_start,
            clock_in__date__lte=period_end,
            status="approved",
        )

        totals = approved.aggregate(
            total_hours=Sum("hours"),
            total_ot=Sum("overtime_hours"),
        )
        total_hours = float(totals["total_hours"] or 0)
        total_ot = float(totals["total_ot"] or 0)

        return {
            "total_hours_mtd": total_hours,
            "overtime_hours_mtd": total_ot,
            "overtime_rate": round(total_ot / total_hours * 100, 1) if total_hours > 0 else 0,
        }

    @staticmethod
    def _labor_kpis(org, period_start, period_end):
        summary = KPIService._labor_summary(org, period_start, period_end)
        kpis = [
            ("Total Labor Hours MTD", "labor", summary["total_hours_mtd"], None, "hrs"),
            ("Overtime Hours MTD", "labor", summary["overtime_hours_mtd"], None, "hrs"),
            ("Overtime Rate MTD", "labor", summary["overtime_rate"], 15.0, "%"),
        ]
        return KPIService._upsert_kpis(org, kpis, period_start, period_end)

    # ------------------------------------------------------------------ #
    # Safety
    # ------------------------------------------------------------------ #

    @staticmethod
    def _safety_summary(org, period_start, period_end):
        from apps.quality_safety.models import SafetyIncident

        incidents = SafetyIncident.objects.filter(
            organization=org,
            incident_date__gte=period_start,
            incident_date__lte=period_end,
        )
        total = incidents.count()
        recordable = incidents.filter(osha_reportable=True).count()
        lost_time = incidents.filter(severity="lost_time").count()

        return {
            "total_incidents": total,
            "recordable_incidents": recordable,
            "lost_time_incidents": lost_time,
        }

    @staticmethod
    def _safety_kpis(org, period_start, period_end):
        summary = KPIService._safety_summary(org, period_start, period_end)
        kpis = [
            ("Safety Incidents MTD", "safety", summary["total_incidents"], 0, "count"),
            ("Recordable Incidents MTD", "safety", summary["recordable_incidents"], 0, "count"),
            ("Lost Time Incidents MTD", "safety", summary["lost_time_incidents"], 0, "count"),
        ]
        return KPIService._upsert_kpis(org, kpis, period_start, period_end)

    # ------------------------------------------------------------------ #
    # Service
    # ------------------------------------------------------------------ #

    @staticmethod
    def _service_summary(org):
        from apps.service.models import ServiceTicket, Warranty

        open_tickets = ServiceTicket.objects.filter(
            organization=org,
            status__in=["new", "assigned", "in_progress"],
        ).count()

        emergency_tickets = ServiceTicket.objects.filter(
            organization=org,
            priority="emergency",
            status__in=["new", "assigned", "in_progress"],
        ).count()

        active_warranties = Warranty.objects.filter(
            organization=org,
            status="active",
        ).count()

        return {
            "open_tickets": open_tickets,
            "emergency_tickets": emergency_tickets,
            "active_warranties": active_warranties,
        }

    @staticmethod
    def _service_kpis(org, period_start, period_end):
        summary = KPIService._service_summary(org)
        kpis = [
            ("Open Service Tickets", "service", summary["open_tickets"], None, "count"),
            ("Emergency Tickets", "service", summary["emergency_tickets"], 0, "count"),
            ("Active Warranties", "service", summary["active_warranties"], None, "count"),
        ]
        return KPIService._upsert_kpis(org, kpis, period_start, period_end)

    # ------------------------------------------------------------------ #
    # Upsert helper
    # ------------------------------------------------------------------ #

    @staticmethod
    def _upsert_kpis(org, kpi_tuples, period_start, period_end):
        """Create or update KPI records. kpi_tuples: [(name, category, value, target, unit)]"""
        from .models import KPI

        results = []
        for name, category, value, target, unit in kpi_tuples:
            try:
                decimal_value = Decimal(str(value)) if value is not None else None
                decimal_target = Decimal(str(target)) if target is not None else None
            except InvalidOperation:
                decimal_value = None
                decimal_target = None

            kpi, _ = KPI.objects.update_or_create(
                organization=org,
                name=name,
                category=category,
                period_start=period_start,
                period_end=period_end,
                project=None,
                defaults={
                    "value": decimal_value,
                    "target": decimal_target,
                    "unit": unit,
                },
            )
            results.append(kpi)
        return results


class ReportService:
    """Execute saved report definitions and return structured data."""

    REPORT_RUNNERS = {}

    @staticmethod
    def run_report(report):
        """Execute a report and cache the result."""
        runner = ReportService._get_runner(report.report_type)
        result = runner(report)
        report.last_run_at = timezone.now()
        report.last_run_result = result
        report.save(update_fields=["last_run_at", "last_run_result", "updated_at"])
        return result

    @staticmethod
    def _get_runner(report_type):
        runners = {
            "financial": ReportService._run_financial,
            "project": ReportService._run_project,
            "labor": ReportService._run_labor,
            "safety": ReportService._run_safety,
            "service": ReportService._run_service,
            "custom": ReportService._run_custom,
        }
        return runners.get(report_type, ReportService._run_custom)

    @staticmethod
    def _run_financial(report):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org is None:
            return {"error": "No organization context"}

        config = report.query_config or {}
        months = int(config.get("months", 3))
        period_start = (timezone.now().date().replace(day=1) - timedelta(days=30 * (months - 1)))
        period_end = timezone.now().date()

        from apps.financials.models import Invoice, Expense
        from django.db.models import Sum

        invoices = (
            Invoice.objects.filter(
                organization=org,
                issue_date__range=(period_start, period_end),
            )
            .values("status")
            .annotate(count=Count("id"), total=Sum("total"))
        )

        expenses = (
            Expense.objects.filter(
                organization=org,
                expense_date__range=(period_start, period_end),
            )
            .values("expense_type")
            .annotate(count=Count("id"), total=Sum("amount"))
        )

        return {
            "report_type": "financial",
            "period": {"start": str(period_start), "end": str(period_end)},
            "invoices_by_status": list(invoices),
            "expenses_by_category": list(expenses),
        }

    @staticmethod
    def _run_project(report):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org is None:
            return {"error": "No organization context"}

        from apps.projects.models import Project

        projects = (
            Project.objects.filter(organization=org)
            .values("status", "health_status")
            .annotate(count=Count("id"))
        )

        return {
            "report_type": "project",
            "projects_by_status_health": list(projects),
            "total": Project.objects.filter(organization=org).count(),
        }

    @staticmethod
    def _run_labor(report):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org is None:
            return {"error": "No organization context"}

        config = report.query_config or {}
        months = int(config.get("months", 1))
        period_start = timezone.now().date().replace(day=1)
        if months > 1:
            period_start = (period_start - timedelta(days=30 * (months - 1))).replace(day=1)
        period_end = timezone.now().date()

        from apps.field_ops.models import TimeEntry

        by_project = (
            TimeEntry.objects.filter(
                organization=org,
                clock_in__date__range=(period_start, period_end),
                status="approved",
            )
            .values("project__name", "project_id")
            .annotate(
                total_hours=Sum("hours"),
                overtime_hours=Sum("overtime_hours"),
                entries=Count("id"),
            )
            .order_by("-total_hours")
        )

        return {
            "report_type": "labor",
            "period": {"start": str(period_start), "end": str(period_end)},
            "labor_by_project": list(by_project),
        }

    @staticmethod
    def _run_safety(report):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org is None:
            return {"error": "No organization context"}

        config = report.query_config or {}
        months = int(config.get("months", 3))
        period_start = (timezone.now().date().replace(day=1) - timedelta(days=30 * (months - 1)))
        period_end = timezone.now().date()

        from apps.quality_safety.models import SafetyIncident, Inspection

        incidents = (
            SafetyIncident.objects.filter(
                organization=org,
                incident_date__range=(period_start, period_end),
            )
            .values("severity", "incident_type")
            .annotate(count=Count("id"))
        )

        inspections = (
            Inspection.objects.filter(
                organization=org,
                inspection_date__range=(period_start, period_end),
            )
            .values("status")
            .annotate(count=Count("id"))
        )

        return {
            "report_type": "safety",
            "period": {"start": str(period_start), "end": str(period_end)},
            "incidents_by_type": list(incidents),
            "inspections_by_status": list(inspections),
        }

    @staticmethod
    def _run_service(report):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org is None:
            return {"error": "No organization context"}

        from apps.service.models import ServiceTicket, Warranty, WarrantyClaim

        tickets = (
            ServiceTicket.objects.filter(organization=org)
            .values("status", "priority")
            .annotate(count=Count("id"))
        )

        claims = (
            WarrantyClaim.objects.filter(organization=org)
            .values("status")
            .annotate(count=Count("id"))
        )

        return {
            "report_type": "service",
            "tickets_by_status_priority": list(tickets),
            "warranty_claims_by_status": list(claims),
            "active_warranties": Warranty.objects.filter(
                organization=org, status="active"
            ).count(),
        }

    @staticmethod
    def _run_custom(report):
        """Placeholder for custom SQL/ORM reports defined via query_config."""
        return {
            "report_type": "custom",
            "note": "Custom report execution not yet configured.",
            "query_config": report.query_config,
        }


class ExportService:
    """Export report results and KPI data to CSV."""

    @staticmethod
    def export_kpis_to_csv(organization, category=None):
        """Return a CSV bytes buffer of KPI data for the org."""
        from .models import KPI

        qs = KPI.objects.filter(organization=organization).order_by(
            "-period_end", "category", "name"
        )
        if category:
            qs = qs.filter(category=category)

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["name", "category", "value", "target", "unit",
                        "trend", "variance_percent", "period_start", "period_end"],
        )
        writer.writeheader()
        for kpi in qs:
            writer.writerow({
                "name": kpi.name,
                "category": kpi.category,
                "value": kpi.value,
                "target": kpi.target,
                "unit": kpi.unit,
                "trend": kpi.trend,
                "variance_percent": kpi.variance_percent,
                "period_start": kpi.period_start,
                "period_end": kpi.period_end,
            })
        return output.getvalue().encode("utf-8")

    @staticmethod
    def export_report_result_to_csv(report):
        """Flatten a report's last_run_result to CSV. Returns bytes."""
        result = report.last_run_result
        if not result:
            return b""

        output = io.StringIO()
        # Find the first list value to export
        for key, val in result.items():
            if isinstance(val, list) and val:
                writer = csv.DictWriter(output, fieldnames=list(val[0].keys()))
                writer.writeheader()
                writer.writerows(val)
                break
        return output.getvalue().encode("utf-8")
