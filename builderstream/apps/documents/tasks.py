"""
Document & Photo Control Celery tasks.

Tasks:
  generate_thumbnails        — On-demand, generate thumbnail for a newly uploaded photo
  check_rfi_due_dates        — Daily, notify assignees of RFIs due within 3 days
  check_document_expirations — Weekly, flag or archive documents past expiry
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_thumbnails(self, photo_id: str):
    """
    Generate a 400px thumbnail for a photo and save the thumbnail_key back.

    Args:
        photo_id: UUID string of the Photo record
    """
    from apps.documents.models import Photo
    from apps.documents.services import PhotoProcessingService

    try:
        photo = Photo.objects.get(pk=photo_id)
    except Photo.DoesNotExist:
        logger.warning("generate_thumbnails: Photo %s not found.", photo_id)
        return False

    if photo.thumbnail_key:
        # Already has a thumbnail
        return True

    try:
        thumbnail_key = PhotoProcessingService.generate_thumbnail(
            source_key=photo.file_key,
            organization_id=str(photo.organization_id),
            project_id=str(photo.project_id),
        )
        if thumbnail_key:
            photo.thumbnail_key = thumbnail_key
            photo.save(update_fields=["thumbnail_key"])
            logger.info("Thumbnail generated for photo %s: %s", photo_id, thumbnail_key)
            return True
    except Exception as exc:
        logger.error("generate_thumbnails failed for photo %s: %s", photo_id, exc)
        raise self.retry(exc=exc)

    return False


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def check_rfi_due_dates(self):
    """
    Daily task — notify assignees of RFIs due within 3 days.

    Sends notifications for open/unanswered RFIs approaching their due date.
    """
    from apps.documents.models import RFI

    today = timezone.now().date()
    warning_date = today + timezone.timedelta(days=3)

    # RFIs due within 3 days that are still open or draft
    due_rfis = RFI.objects.filter(
        due_date__lte=warning_date,
        due_date__gte=today,
        status__in=[RFI.Status.OPEN, RFI.Status.DRAFT],
    ).select_related("project", "assigned_to", "organization")

    notified_count = 0
    for rfi in due_rfis:
        if not rfi.assigned_to or not rfi.assigned_to.email:
            continue
        try:
            days_left = (rfi.due_date - today).days
            logger.info(
                "RFI-%03d '%s' due in %d day(s) — assignee: %s",
                rfi.rfi_number,
                rfi.subject,
                days_left,
                rfi.assigned_to.email,
            )
            # Email sending would go here via send_mail or notification service
            notified_count += 1
        except Exception as exc:
            logger.error("Failed to notify for RFI %s: %s", rfi.pk, exc)

    logger.info("check_rfi_due_dates complete — notified: %d", notified_count)
    return {"notified": notified_count}


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def check_document_expirations(self):
    """
    Weekly task — archive documents that have passed their expiry.

    Documents with status=ACTIVE and an expiry date in the past
    are transitioned to ARCHIVED status.
    """
    from apps.documents.models import Document

    # This is a placeholder — Document model doesn't have expiry_date yet.
    # When an expiry_date field is added, implement:
    # expired = Document.objects.filter(
    #     status=Document.Status.ACTIVE,
    #     expiry_date__lt=timezone.now().date(),
    # )
    # count = expired.update(status=Document.Status.ARCHIVED)
    # logger.info("check_document_expirations: archived %d documents", count)

    logger.info("check_document_expirations: no expiry logic configured yet.")
    return {"archived": 0}
