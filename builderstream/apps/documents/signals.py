"""
Document & Photo Control signals.

Handlers:
  cache_submittal_old_status   — pre_save Submittal, caches old status
  log_submittal_status_change  — post_save Submittal, logs activity on status transition
  cache_rfi_old_status         — pre_save RFI, caches old status
  log_rfi_status_change        — post_save RFI, logs activity on status transition
  notify_on_document_upload    — post_save Document (created), queues thumbnail/notification
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="documents.RFI")
def cache_rfi_old_status(sender, instance, **kwargs):
    """Cache the old status before saving so post_save can detect changes."""
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender="documents.RFI")
def log_rfi_status_change(sender, instance, created, **kwargs):
    """Log activity when RFI status changes."""
    if created:
        return

    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        try:
            from apps.projects.models import ActivityLog
            ActivityLog.objects.create(
                organization=instance.organization,
                project=instance.project,
                activity_type="RFI_STATUS_CHANGED",
                description=f"RFI-{instance.rfi_number:03d} '{instance.subject}': {old_status} → {instance.status}",
                metadata={
                    "rfi_id": str(instance.pk),
                    "rfi_number": instance.rfi_number,
                    "old_status": old_status,
                    "new_status": instance.status,
                },
            )
        except Exception as exc:
            logger.warning("Failed to log RFI status change: %s", exc)


@receiver(pre_save, sender="documents.Submittal")
def cache_submittal_old_status(sender, instance, **kwargs):
    """Cache the old status before saving so post_save can detect changes."""
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender="documents.Submittal")
def log_submittal_status_change(sender, instance, created, **kwargs):
    """Log activity when Submittal status changes."""
    if created:
        return

    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        try:
            from apps.projects.models import ActivityLog
            ActivityLog.objects.create(
                organization=instance.organization,
                project=instance.project,
                activity_type="SUBMITTAL_STATUS_CHANGED",
                description=(
                    f"Submittal SUB-{instance.submittal_number:03d} '{instance.title}': "
                    f"{old_status} \u2192 {instance.status}"
                ),
                metadata={
                    "submittal_id": str(instance.pk),
                    "submittal_number": instance.submittal_number,
                    "old_status": old_status,
                    "new_status": instance.status,
                },
            )
        except Exception as exc:
            logger.warning("Failed to log Submittal status change: %s", exc)


@receiver(post_save, sender="documents.Document")
def notify_on_document_upload(sender, instance, created, **kwargs):
    """
    On new document upload, log activity and notify team members
    who require_acknowledgment documents.
    """
    if not created:
        return

    try:
        from apps.projects.models import ActivityLog
        if instance.project:
            ActivityLog.objects.create(
                organization=instance.organization,
                project=instance.project,
                activity_type="DOCUMENT_UPLOADED",
                description=f"Document uploaded: {instance.title} (v{instance.version})",
                metadata={
                    "document_id": str(instance.pk),
                    "title": instance.title,
                    "file_name": instance.file_name,
                    "requires_acknowledgment": instance.requires_acknowledgment,
                },
            )
    except Exception as exc:
        logger.warning("Failed to log document upload activity: %s", exc)
