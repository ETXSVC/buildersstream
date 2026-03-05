# Signal handlers that fire notifications for key domain events.
# Import additional signals from other apps here to keep notification logic
# centralized.

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="projects.Project")
def on_project_status_changed(sender, instance, created, **kwargs):
    """Notify org admins when a project changes status."""
    if created:
        return
    if not hasattr(instance, "_pre_save_status"):
        return
    if instance._pre_save_status == instance.status:
        return

    from apps.notifications.services import NotificationService
    from apps.notifications.models import Notification

    NotificationService.notify_org_admins(
        org=instance.org,
        notification_type=Notification.NotificationType.PROJECT_STATUS_CHANGED,
        title=f"Project status changed: {instance.name}",
        body=f"Status changed from {instance._pre_save_status} to {instance.status}",
        data={
            "project_id": str(instance.pk),
            "url": f"/projects/{instance.pk}/",
            "old_status": instance._pre_save_status,
            "new_status": instance.status,
        },
    )
