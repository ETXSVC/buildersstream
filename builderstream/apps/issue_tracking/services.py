"""Issue Tracking services — number generation, SLA calculation, escalation."""
import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


class IssueNumberService:
    """Generate sequential issue numbers per organization."""

    @staticmethod
    def generate(org):
        """Return next issue number like ISS-00001."""
        from .models import Issue

        count = Issue.objects.for_organization(org).count() + 1
        return f"ISS-{count:05d}"


class SLAService:
    """Calculate and track SLA compliance for issues."""

    @staticmethod
    def calculate_due_dates(issue):
        """Compute response and resolution due dates from IssueType SLA config."""
        if not issue.issue_type:
            return

        now = timezone.now()
        issue.sla_response_due_at = now + timedelta(hours=issue.issue_type.sla_response_hours)
        issue.sla_resolution_due_at = now + timedelta(hours=issue.issue_type.sla_resolution_hours)

    @staticmethod
    def check_sla_breaches():
        """Mark SLA breaches and trigger escalations. Called by Celery."""
        from .models import Issue

        now = timezone.now()
        open_statuses = [
            Issue.Status.NEW,
            Issue.Status.OPEN,
            Issue.Status.IN_PROGRESS,
            Issue.Status.PENDING,
        ]

        # Response SLA breaches
        response_breached = Issue.objects.unscoped().filter(
            status__in=open_statuses,
            sla_response_due_at__lt=now,
            sla_response_met__isnull=True,
            first_responded_at__isnull=True,
        )
        breach_count = response_breached.count()
        if breach_count:
            response_breached.update(sla_response_met=False)
            logger.info("Marked %d response SLA breaches", breach_count)

        # Resolution SLA breaches
        resolution_breached = Issue.objects.unscoped().filter(
            status__in=open_statuses,
            sla_resolution_due_at__lt=now,
            sla_resolution_met__isnull=True,
        )
        resolution_count = resolution_breached.count()
        if resolution_count:
            resolution_breached.update(sla_resolution_met=False)
            logger.info("Marked %d resolution SLA breaches", resolution_count)

        # Trigger escalations for newly breached issues
        for issue in response_breached:
            EscalationService.process_rules(issue)

    @staticmethod
    def mark_response_met(issue):
        """Record first response and check SLA compliance."""
        if issue.first_responded_at:
            return
        now = timezone.now()
        issue.first_responded_at = now
        if issue.sla_response_due_at:
            issue.sla_response_met = now <= issue.sla_response_due_at
        issue.save(update_fields=["first_responded_at", "sla_response_met"])

    @staticmethod
    def mark_resolution(issue):
        """Record resolution time and check resolution SLA."""
        now = timezone.now()
        issue.resolved_at = now
        if issue.sla_resolution_due_at:
            issue.sla_resolution_met = now <= issue.sla_resolution_due_at
        issue.save(update_fields=["resolved_at", "sla_resolution_met"])


class EscalationService:
    """Evaluate and execute escalation rules against issues."""

    @staticmethod
    def process_rules(issue):
        """Check all active escalation rules for an issue and execute matching ones."""
        from .models import EscalationRule

        rules = EscalationRule.objects.for_organization(issue.organization).filter(is_active=True)
        now = timezone.now()

        for rule in rules:
            try:
                if EscalationService._matches(issue, rule, now):
                    EscalationService._execute(issue, rule)
            except Exception:
                logger.exception(
                    "Escalation rule %s failed for issue %s", rule.pk, issue.pk
                )

    @staticmethod
    def _matches(issue, rule, now):
        """Return True if the issue matches the rule's trigger condition."""
        condition = rule.trigger_condition
        ctype = condition.get("condition_type")
        hours = condition.get("hours_threshold", 0)
        priority_filter = condition.get("priority_filter")

        if priority_filter and issue.priority != priority_filter:
            return False

        if ctype == "sla_breach":
            return issue.sla_response_met is False or issue.sla_resolution_met is False

        if ctype == "no_response":
            if issue.first_responded_at:
                return False
            if issue.created_at and hours:
                return (now - issue.created_at).total_seconds() / 3600 >= hours

        if ctype == "status_stale":
            if issue.updated_at and hours:
                return (now - issue.updated_at).total_seconds() / 3600 >= hours

        return False

    @staticmethod
    def _execute(issue, rule):
        """Execute escalation action."""
        from apps.accounts.models import User

        action = rule.action_type
        config = rule.action_config

        if action == "reassign":
            assignee_id = config.get("assignee_id")
            if assignee_id:
                try:
                    assignee = User.objects.get(pk=assignee_id)
                    issue.assignee = assignee
                    issue.save(update_fields=["assignee"])
                    logger.info("Escalated issue %s: reassigned to %s", issue.pk, assignee_id)
                except User.DoesNotExist:
                    logger.warning("Escalation assignee %s not found", assignee_id)

        elif action == "change_priority":
            new_priority = config.get("priority")
            if new_priority:
                issue.priority = new_priority
                issue.save(update_fields=["priority"])
                logger.info("Escalated issue %s: priority changed to %s", issue.pk, new_priority)

        elif action == "notify":
            # Log only — full notification integration requires NotificationService
            user_ids = config.get("user_ids", [])
            logger.info("Escalation notify: issue %s → users %s", issue.pk, user_ids)


class SLAComplianceReport:
    """Aggregate SLA compliance statistics."""

    @staticmethod
    def for_organization(org):
        """Return SLA compliance summary for the org."""
        from .models import Issue

        qs = Issue.objects.for_organization(org)
        total = qs.count()
        response_met = qs.filter(sla_response_met=True).count()
        response_breached = qs.filter(sla_response_met=False).count()
        resolution_met = qs.filter(sla_resolution_met=True).count()
        resolution_breached = qs.filter(sla_resolution_met=False).count()

        def pct(numerator, denominator):
            return round(numerator / denominator * 100, 1) if denominator else 0

        return {
            "total_issues": total,
            "response_sla": {
                "met": response_met,
                "breached": response_breached,
                "compliance_pct": pct(response_met, response_met + response_breached),
            },
            "resolution_sla": {
                "met": resolution_met,
                "breached": resolution_breached,
                "compliance_pct": pct(resolution_met, resolution_met + resolution_breached),
            },
            "by_status": {
                s: qs.filter(status=s).count()
                for s in ["new", "open", "in_progress", "pending", "resolved", "closed"]
            },
            "by_priority": {
                p: qs.filter(priority=p).count()
                for p in ["critical", "high", "medium", "low"]
            },
        }
