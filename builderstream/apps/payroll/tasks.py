"""Payroll Celery tasks."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="payroll.check_certification_expirations")
def check_certification_expirations():
    """Alert on employee certifications expiring within 30 days.

    Runs daily. Logs a warning for each expiring certification so that
    notification/email logic can be layered on top in future iterations.
    """
    from apps.tenants.models import Organization
    from .services import WorkforceService

    org_ids = list(Organization.objects.filter(is_active=True).values_list("id", flat=True))
    total = 0
    for org_id in org_ids:
        try:
            org = Organization.objects.get(pk=org_id)
            expiring = WorkforceService.get_expiring_certifications(org, days_ahead=30)
            for item in expiring:
                logger.warning(
                    "Certification expiring in %d days: %s — %s (employee %s)",
                    item["days_until_expiry"],
                    item["cert_name"],
                    item["employee_name"],
                    item["employee_id"],
                )
                total += 1
        except Exception:
            logger.exception("Error checking certification expirations for org %s", org_id)

    logger.info("check_certification_expirations: %d expiring certifications found", total)
    return total


@shared_task(name="payroll.prevailing_wage_compliance_check")
def prevailing_wage_compliance_check():
    """Re-run prevailing wage compliance on all DRAFT certified payroll reports.

    Runs weekly. Refreshes compliance_issues so reports stay current.
    """
    from .models import CertifiedPayrollReport
    from .services import CertifiedPayrollService

    draft_reports = CertifiedPayrollReport.objects.filter(
        status=CertifiedPayrollReport.ReportStatus.DRAFT,
    ).select_related("payroll_run", "project")

    updated = 0
    for report in draft_reports:
        try:
            CertifiedPayrollService.generate_report(
                payroll_run=report.payroll_run,
                project=report.project,
                report_type=report.report_type,
            )
            updated += 1
        except Exception:
            logger.exception(
                "Error running compliance check for certified report %s", report.pk
            )

    logger.info("prevailing_wage_compliance_check: %d reports refreshed", updated)
    return updated
