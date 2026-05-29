"""
Document & Photo Control services.

4 service classes:
  FileUploadService       — Presigned S3 upload/download URLs, file validation
  VersionControlService   — Document versioning chain management
  RFIService              — RFI auto-numbering, routing, distribution
  PhotoProcessingService  — EXIF extraction, thumbnail generation, AI tag stubs
"""

import logging
import uuid as _uuid
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Allowed MIME types for documents and photos
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/tiff",
    "image/heic",
    "video/mp4",
    "video/quicktime",
    "application/zip",
    "application/x-zip-compressed",
    "application/octet-stream",
}

ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/heic", "image/tiff"}

MAX_DOCUMENT_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB
MAX_PHOTO_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
PRESIGNED_URL_EXPIRY_SECONDS = 3600  # 1 hour


def _get_s3_client():
    """Return a boto3 S3 client using Django settings."""
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


class FileUploadService:
    """
    Generate presigned S3 upload and download URLs for direct browser-to-S3 uploads.
    """

    @staticmethod
    def generate_upload_url(organization_id, project_id, file_name, content_type, file_type="document"):
        """
        Generate a presigned S3 PUT URL for direct browser upload.

        Args:
            organization_id: UUID string of the organization
            project_id: UUID string of the project (or None for org-level)
            file_name: Original filename
            content_type: MIME type of the file
            file_type: "document" or "photo"

        Returns:
            dict: {upload_url, file_key, expires_in}

        Raises:
            ValueError: If content type not allowed or file type invalid
        """
        allowed = ALLOWED_PHOTO_TYPES if file_type == "photo" else ALLOWED_DOCUMENT_TYPES
        if content_type not in allowed:
            raise ValueError(f"File type '{content_type}' is not allowed.")

        # Build S3 key:  org/{org_id}/{photos|documents}/{project_id}/{uuid}/{filename}
        folder = "photos" if file_type == "photo" else "documents"
        proj_segment = str(project_id) if project_id else "org-level"
        unique_id = str(_uuid.uuid4())
        file_key = f"org/{organization_id}/{folder}/{proj_segment}/{unique_id}/{file_name}"

        bucket = settings.AWS_STORAGE_BUCKET_NAME

        try:
            s3 = _get_s3_client()
            upload_url = s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket,
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
            )
        except ClientError as exc:
            logger.error("Failed to generate presigned upload URL: %s", exc)
            raise ValueError(f"Could not generate upload URL: {exc}")

        return {
            "upload_url": upload_url,
            "file_key": file_key,
            "expires_in": PRESIGNED_URL_EXPIRY_SECONDS,
        }

    @staticmethod
    def generate_bulk_upload_urls(organization_id, project_id, files):
        """
        Generate presigned upload URLs for multiple photo files.

        Args:
            files: List of dicts with {file_name, content_type}

        Returns:
            List of {file_name, upload_url, file_key, error}
        """
        results = []
        for f in files:
            try:
                result = FileUploadService.generate_upload_url(
                    organization_id=organization_id,
                    project_id=project_id,
                    file_name=f["file_name"],
                    content_type=f.get("content_type", "image/jpeg"),
                    file_type="photo",
                )
                result["file_name"] = f["file_name"]
                results.append(result)
            except ValueError as exc:
                results.append({"file_name": f["file_name"], "error": str(exc)})
        return results

    @staticmethod
    def generate_download_url(file_key, file_name=None, expiry=None):
        """
        Generate a presigned S3 GET URL for downloading a document.

        Args:
            file_key: S3 object key
            file_name: Override filename for Content-Disposition header
            expiry: TTL in seconds (default: PRESIGNED_URL_EXPIRY_SECONDS)

        Returns:
            str: Presigned download URL
        """
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        expiry = expiry or PRESIGNED_URL_EXPIRY_SECONDS

        params = {"Bucket": bucket, "Key": file_key}
        if file_name:
            params["ResponseContentDisposition"] = f'attachment; filename="{file_name}"'

        try:
            s3 = _get_s3_client()
            return s3.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expiry,
            )
        except ClientError as exc:
            logger.error("Failed to generate presigned download URL for %s: %s", file_key, exc)
            raise ValueError(f"Could not generate download URL: {exc}")

    @staticmethod
    def delete_s3_object(file_key):
        """Delete an object from S3 (used when document record is deleted)."""
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        try:
            s3 = _get_s3_client()
            s3.delete_object(Bucket=bucket, Key=file_key)
            logger.info("Deleted S3 object: %s", file_key)
        except ClientError as exc:
            logger.warning("Failed to delete S3 object %s: %s", file_key, exc)


class VersionControlService:
    """
    Document version management — maintains an immutable chain of versions.
    """

    @staticmethod
    def create_new_version(existing_document, file_key, file_name, file_size, content_type, uploaded_by):
        """
        Upload a new version of a document.

        Steps:
          1. Mark existing document as SUPERSEDED and is_current_version=False
          2. Create a new Document record referencing the old one via previous_version

        Args:
            existing_document: Document instance (must be is_current_version=True)
            file_key: S3 key of the newly uploaded file
            file_name: Original filename of the new version
            file_size: File size in bytes
            content_type: MIME type
            uploaded_by: User instance

        Returns:
            New Document instance (current version)
        """
        from apps.documents.models import Document

        if not existing_document.is_current_version:
            raise ValueError("Can only create a new version from the current version.")

        # Supersede existing
        existing_document.status = Document.Status.SUPERSEDED
        existing_document.is_current_version = False
        existing_document.save(update_fields=["status", "is_current_version", "updated_at"])

        # Create new version
        new_version = Document.objects.create(
            organization=existing_document.organization,
            created_by=uploaded_by,
            folder=existing_document.folder,
            project=existing_document.project,
            title=existing_document.title,
            description=existing_document.description,
            file_key=file_key,
            file_name=file_name,
            file_size=file_size,
            content_type=content_type,
            version=existing_document.version + 1,
            is_current_version=True,
            previous_version=existing_document,
            uploaded_by=uploaded_by,
            tags=existing_document.tags,
            requires_acknowledgment=existing_document.requires_acknowledgment,
            status=Document.Status.ACTIVE,
        )
        return new_version

    @staticmethod
    def get_version_history(document):
        """
        Return all versions of a document in reverse-chronological order.

        Traverses the previous_version chain up to the root.
        """
        from apps.documents.models import Document

        # Start from the current version, walk back
        versions = []
        current = document if document.is_current_version else (
            Document.objects.filter(
                project=document.project,
                title=document.title,
                is_current_version=True,
            ).first() or document
        )
        versions.append(current)
        node = current
        while node.previous_version_id:
            node = Document.objects.get(pk=node.previous_version_id)
            versions.append(node)

        return versions


class RFIService:
    """
    RFI auto-numbering, routing, answer distribution, and activity logging.
    """

    @staticmethod
    def get_next_rfi_number(project):
        """Auto-increment RFI number per project."""
        from apps.documents.models import RFI
        last = RFI.objects.filter(project=project).order_by("-rfi_number").values("rfi_number").first()
        return (last["rfi_number"] + 1) if last else 1

    @staticmethod
    def create_rfi(project, subject, question, requested_by, assigned_to=None,
                   priority="NORMAL", due_date=None, distribution_users=None):
        """
        Create a new RFI with auto-incremented number.

        Args:
            distribution_users: List of User instances to notify on answer

        Returns:
            RFI instance
        """
        from apps.documents.models import RFI

        rfi_number = RFIService.get_next_rfi_number(project)
        rfi = RFI.objects.create(
            organization=project.organization,
            created_by=requested_by,
            project=project,
            rfi_number=rfi_number,
            subject=subject,
            question=question,
            status=RFI.Status.OPEN,
            priority=priority,
            requested_by=requested_by,
            assigned_to=assigned_to,
            due_date=due_date,
        )
        if distribution_users:
            rfi.distribution_list.set(distribution_users)

        RFIService._log_rfi_activity(rfi, requested_by, "created", f"RFI-{rfi_number:03d} opened: {subject}")
        return rfi

    @staticmethod
    def answer_rfi(rfi, answer_text, answered_by):
        """
        Record an answer for an RFI and distribute to the distribution list.

        Returns:
            Updated RFI instance
        """
        from apps.documents.models import RFI

        rfi.answer = answer_text
        rfi.status = RFI.Status.ANSWERED
        rfi.answered_at = timezone.now()
        rfi.save(update_fields=["answer", "status", "answered_at", "updated_at"])

        RFIService._log_rfi_activity(rfi, answered_by, "updated", f"RFI-{rfi.rfi_number:03d} answered by {answered_by}")
        RFIService._distribute_answer(rfi)
        return rfi

    @staticmethod
    def close_rfi(rfi, closed_by):
        """Close a resolved RFI."""
        from apps.documents.models import RFI

        if rfi.status not in (RFI.Status.ANSWERED, RFI.Status.OPEN):
            raise ValueError(f"Cannot close an RFI with status '{rfi.status}'.")

        rfi.status = RFI.Status.CLOSED
        rfi.save(update_fields=["status", "updated_at"])
        RFIService._log_rfi_activity(rfi, closed_by, "updated", f"RFI-{rfi.rfi_number:03d} closed")
        return rfi

    @staticmethod
    def _distribute_answer(rfi):
        """Send answer notification to distribution list members."""
        from django.conf import settings
        from django.core.mail import send_mail

        recipients = list(
            rfi.distribution_list.filter(email__isnull=False).values_list("email", flat=True)
        )
        if not recipients:
            return

        try:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")
            send_mail(
                subject=f"RFI-{rfi.rfi_number:03d} Answered: {rfi.subject}",
                message=(
                    f"RFI-{rfi.rfi_number:03d} has been answered.\n\n"
                    f"Question: {rfi.question}\n\n"
                    f"Answer: {rfi.answer}"
                ),
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=True,
            )
        except Exception as exc:
            logger.warning("Failed to distribute RFI answer: %s", exc)

    @staticmethod
    def _log_rfi_activity(rfi, user, action, description):
        try:
            from apps.projects.models import ActivityLog
            ActivityLog.objects.create(
                organization=rfi.organization,
                project=rfi.project,
                user=user,
                action=action,
                description=description,
                changes={"rfi_id": str(rfi.pk), "rfi_number": rfi.rfi_number},
            )
        except Exception as exc:
            logger.warning("Failed to log RFI activity: %s", exc)


class PhotoProcessingService:
    """
    Photo upload post-processing: EXIF extraction, thumbnail generation, AI tag stubs.
    """

    THUMBNAIL_WIDTH = 400  # pixels

    @staticmethod
    def extract_exif_data(file_key):
        """
        Extract EXIF metadata from a photo in S3.

        Returns:
            dict: {taken_at, latitude, longitude} — values may be None if not in EXIF
        """
        result = {"taken_at": None, "latitude": None, "longitude": None}

        try:
            from io import BytesIO

            from PIL import Image
            from PIL.ExifTags import TAGS

            s3 = _get_s3_client()
            bucket = settings.AWS_STORAGE_BUCKET_NAME

            # Stream just the first 64KB to get EXIF without downloading full file
            response = s3.get_object(
                Bucket=bucket, Key=file_key, Range="bytes=0-65535"
            )
            data = response["Body"].read()
            img = Image.open(BytesIO(data))
            exif_data = img._getexif()

            if not exif_data:
                return result

            # Map EXIF tag IDs to names
            exif_named = {TAGS.get(k, k): v for k, v in exif_data.items()}

            # Timestamp
            dt_str = exif_named.get("DateTimeOriginal") or exif_named.get("DateTime")
            if dt_str:
                from datetime import datetime
                try:
                    taken_at = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                    from django.utils.timezone import make_aware
                    result["taken_at"] = make_aware(taken_at)
                except ValueError:
                    pass

            # GPS
            gps_info = exif_named.get("GPSInfo")
            if gps_info:
                result["latitude"], result["longitude"] = PhotoProcessingService._parse_gps(gps_info)

        except ImportError:
            logger.info("Pillow not installed — skipping EXIF extraction")
        except Exception as exc:
            logger.warning("EXIF extraction failed for %s: %s", file_key, exc)

        return result

    @staticmethod
    def generate_thumbnail(source_key, organization_id, project_id):
        """
        Generate a 400px-wide JPEG thumbnail and upload to S3.

        Returns:
            str: thumbnail S3 key, or "" on failure
        """
        try:
            from io import BytesIO

            from PIL import Image

            s3 = _get_s3_client()
            bucket = settings.AWS_STORAGE_BUCKET_NAME

            response = s3.get_object(Bucket=bucket, Key=source_key)
            img = Image.open(BytesIO(response["Body"].read()))
            img = img.convert("RGB")  # handle RGBA/P modes

            # Maintain aspect ratio
            w_percent = PhotoProcessingService.THUMBNAIL_WIDTH / float(img.width)
            new_height = int(float(img.height) * w_percent)
            thumb = img.resize((PhotoProcessingService.THUMBNAIL_WIDTH, new_height), Image.LANCZOS)

            buffer = BytesIO()
            thumb.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)

            thumb_key = f"org/{organization_id}/thumbnails/{project_id}/{_uuid.uuid4()}.jpg"
            s3.put_object(
                Bucket=bucket,
                Key=thumb_key,
                Body=buffer,
                ContentType="image/jpeg",
            )
            return thumb_key
        except ImportError:
            logger.info("Pillow not installed — skipping thumbnail generation")
            return ""
        except Exception as exc:
            logger.warning("Thumbnail generation failed for %s: %s", source_key, exc)
            return ""

    @staticmethod
    def generate_ai_tags(photo, project_phase=None):
        """
        Generate AI-based category tags for a photo.

        Currently a stub implementation based on project phase and category.
        In production, integrate with AWS Rekognition or similar.

        Returns:
            list: Tag strings
        """
        tags = []

        # Add phase-based tag
        if project_phase:
            tags.append(f"phase:{project_phase.lower().replace(' ', '-')}")

        # Add category-based tags
        category_tags = {
            "PROGRESS": ["construction", "progress", "ongoing"],
            "BEFORE": ["before", "pre-construction", "site"],
            "AFTER": ["after", "completed", "finished"],
            "DEFICIENCY": ["issue", "deficiency", "punch-list"],
            "INSPECTION": ["inspection", "review"],
            "SAFETY": ["safety", "compliance"],
            "DELIVERY": ["delivery", "materials"],
        }
        category = getattr(photo, "category", "OTHER")
        tags.extend(category_tags.get(category, ["general"]))

        return tags

    @staticmethod
    def _parse_gps(gps_info):
        """Convert EXIF GPS IFD to decimal degrees."""
        try:
            from PIL.ExifTags import GPSTAGS
            gps_named = {GPSTAGS.get(k, k): v for k, v in gps_info.items()}

            def to_degrees(dms):
                d, m, s = dms
                return float(d) + float(m) / 60 + float(s) / 3600

            lat = to_degrees(gps_named.get("GPSLatitude", (0, 0, 0)))
            lat_ref = gps_named.get("GPSLatitudeRef", "N")
            lon = to_degrees(gps_named.get("GPSLongitude", (0, 0, 0)))
            lon_ref = gps_named.get("GPSLongitudeRef", "E")

            if lat_ref == "S":
                lat = -lat
            if lon_ref == "W":
                lon = -lon

            return round(lat, 7), round(lon, 7)
        except Exception:
            return None, None
