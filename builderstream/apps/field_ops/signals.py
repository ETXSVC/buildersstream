"""Field operations signals."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_old_daily_log_status = {}


@receiver(pre_save, sender="field_ops.DailyLog")
def cache_daily_log_status(sender, instance, **kwargs):
    """Cache old status before save for change detection."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            _old_daily_log_status[instance.pk] = old.status
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender="field_ops.DailyLog")
def on_daily_log_saved(sender, instance, created, **kwargs):
    """Log activity on creation and status changes."""
    try:
        from apps.projects.models import ActivityLog

        if created:
            ActivityLog.objects.create(
                organization=instance.organization,
                project=instance.project,
                user=instance.created_by,
                activity_type="daily_log_created",
                description=f"Daily log created for {instance.log_date}",
                metadata={"log_id": str(instance.pk), "date": str(instance.log_date)},
            )
        else:
            old_status = _old_daily_log_status.pop(instance.pk, None)
            if old_status and old_status != instance.status:
                ActivityLog.objects.create(
                    organization=instance.organization,
                    project=instance.project,
                    user=instance.submitted_by or instance.created_by,
                    activity_type="daily_log_status_changed",
                    description=(
                        f"Daily log for {instance.log_date} "
                        f"changed from {old_status} to {instance.status}"
                    ),
                    metadata={
                        "log_id": str(instance.pk),
                        "old_status": old_status,
                        "new_status": instance.status,
                    },
                )
    except Exception:
        logger.exception("Error in on_daily_log_saved for log %s", instance.pk)


@receiver(post_save, sender="field_ops.TimeEntry")
def on_time_entry_saved(sender, instance, created, **kwargs):
    """Log when a time entry is approved."""
    try:
        if not created and instance.status == "approved":
            logger.debug(
                "Time entry %s approved: user=%s hours=%s",
                instance.pk, instance.user_id, instance.hours,
            )
    except Exception:
        logger.exception("Error in on_time_entry_saved for entry %s", instance.pk)
