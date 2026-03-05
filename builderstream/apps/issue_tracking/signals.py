"""Issue Tracking signals — SLA calculation, activity logging, status tracking."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Issue

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Issue)
def cache_old_status(sender, instance, **kwargs):
    """Cache previous status for change detection."""
    if instance.pk:
        try:
            old = Issue.objects.unscoped().only("status").get(pk=instance.pk)
            instance._old_status = old.status
        except Issue.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Issue)
def on_issue_save(sender, instance, created, **kwargs):
    """After save: calculate SLA on create, log status changes."""
    if created:
        # Generate issue number if not set
        if not instance.number:
            from .services import IssueNumberService

            number = IssueNumberService.generate(instance.organization)
            Issue.objects.unscoped().filter(pk=instance.pk).update(number=number)
            instance.number = number

        # Calculate SLA due dates
        from .services import SLAService

        SLAService.calculate_due_dates(instance)
        if instance.sla_response_due_at:
            Issue.objects.unscoped().filter(pk=instance.pk).update(
                sla_response_due_at=instance.sla_response_due_at,
                sla_resolution_due_at=instance.sla_resolution_due_at,
            )

        _log_activity(instance, "created", f"Issue {instance.number} created: {instance.title}")

    else:
        old_status = getattr(instance, "_old_status", None)
        if old_status and old_status != instance.status:
            _log_activity(
                instance,
                "status_changed",
                f"Issue {instance.number} status changed from '{old_status}' to '{instance.status}'",
                metadata={"old_status": old_status, "new_status": instance.status},
            )

            # Mark resolution SLA if resolved/closed
            if instance.status in (Issue.Status.RESOLVED, Issue.Status.CLOSED):
                from .services import SLAService

                SLAService.mark_resolution(instance)


def _log_activity(issue, action, description, metadata=None):
    """Write to ActivityLog."""
    try:
        from apps.projects.models import ActivityLog

        ActivityLog.objects.create(
            organization=issue.organization,
            action=action,
            entity_type="issue",
            entity_id=issue.pk,
            description=description,
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("Failed to log activity for issue %s", issue.pk)
