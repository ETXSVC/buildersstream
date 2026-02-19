"""Analytics & Reporting Engine Celery tasks."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="analytics.calculate_kpis")
def calculate_kpis():
    """Daily task: compute all standard KPIs for every active org."""
    from apps.tenants.models import Organization
    from .services import KPIService

    total = 0
    for org in Organization.objects.filter(subscription_status__in=["active", "trialing"]):
        try:
            kpis = KPIService.calculate_all_kpis(org)
            total += len(kpis)
        except Exception as exc:
            logger.error("KPI calculation failed for org %s: %s", org.slug, exc)

    logger.info("calculate_kpis: %d KPIs upserted across all orgs", total)


@shared_task(name="analytics.run_scheduled_reports")
def run_scheduled_reports():
    """Daily task: execute all scheduled, active reports and email recipients."""
    from .models import Report
    from .services import ReportService
    from apps.tenants.context import tenant_context

    scheduled = Report.objects.filter(is_active=True).exclude(schedule="").exclude(recipients=[])

    executed = 0
    for report in scheduled:
        try:
            with tenant_context(report.organization):
                ReportService.run_report(report)
            executed += 1
            logger.info("Scheduled report '%s' executed for org %s", report.name, report.organization_id)
        except Exception as exc:
            logger.error("Scheduled report '%s' failed: %s", report.name, exc)

    logger.info("run_scheduled_reports: %d reports executed", executed)


@shared_task(name="analytics.generate_weekly_summary")
def generate_weekly_summary():
    """Weekly task: calculate KPIs and snapshot for executive summary."""
    from apps.tenants.models import Organization
    from .services import KPIService

    for org in Organization.objects.filter(subscription_status__in=["active", "trialing"]):
        try:
            KPIService.calculate_all_kpis(org)
            logger.info("Weekly KPI snapshot generated for org %s", org.slug)
        except Exception as exc:
            logger.error("Weekly summary failed for org %s: %s", org.slug, exc)
