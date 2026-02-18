"""
Document & Photo Control models.

7 models:
1. DocumentFolder    - Hierarchical folder structure per project or org-level
2. Document          - Versioned document with S3 file key
3. DocumentAcknowledgment - User acknowledgment tracking
4. RFI               - Request For Information with distribution list
5. Submittal         - Construction submittal approval workflow
6. Photo             - Project photos with EXIF, GPS, AI tags
7. PhotoAlbum        - Curated/auto-generated photo collections
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class DocumentFolder(TenantModel):
    """
    Hierarchical folder structure for organizing project documents.

    Folders can be org-level (project=None) or project-specific.
    """

    class FolderType(models.TextChoices):
        GENERAL = "GENERAL", "General"
        PLANS = "PLANS", "Plans & Drawings"
        PERMITS = "PERMITS", "Permits"
        CONTRACTS = "CONTRACTS", "Contracts"
        SUBMITTALS = "SUBMITTALS", "Submittals"
        RFI = "RFI", "RFIs"
        PHOTOS = "PHOTOS", "Photos"
        SAFETY = "SAFETY", "Safety"
        WARRANTY = "WARRANTY", "Warranty"

    class AccessLevel(models.TextChoices):
        ALL_TEAM = "ALL_TEAM", "All Team Members"
        MANAGERS_ONLY = "MANAGERS_ONLY", "Managers Only"
        ADMIN_ONLY = "ADMIN_ONLY", "Admin Only"
        CLIENT_VISIBLE = "CLIENT_VISIBLE", "Client Visible"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="document_folders",
        help_text="Org-level folder if null",
    )
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    folder_type = models.CharField(
        max_length=20, choices=FolderType.choices, default=FolderType.GENERAL
    )
    access_level = models.CharField(
        max_length=20, choices=AccessLevel.choices, default=AccessLevel.ALL_TEAM
    )
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "documents_folder"
        verbose_name = "Document Folder"
        verbose_name_plural = "Document Folders"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["organization", "project"], name="docs_folder_org_proj_idx"),
            models.Index(fields=["organization", "parent"], name="docs_folder_org_parent_idx"),
        ]

    def __str__(self):
        return self.name


class Document(TenantModel):
    """
    Versioned document stored in S3.

    file_key is the S3 object key — presigned URLs generated on demand.
    Versions linked via previous_version FK forming an immutable chain.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        ARCHIVED = "ARCHIVED", "Archived"

    folder = models.ForeignKey(
        DocumentFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    # S3 storage — no FileField, just keys
    file_key = models.CharField(max_length=1000, help_text="S3 object key")
    file_name = models.CharField(max_length=500, help_text="Original filename")
    file_size = models.BigIntegerField(default=0, help_text="Bytes")
    content_type = models.CharField(max_length=200, blank=True, help_text="MIME type")
    # Versioning
    version = models.IntegerField(default=1)
    is_current_version = models.BooleanField(default=True, db_index=True)
    previous_version = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newer_versions",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    tags = models.JSONField(default=list, blank=True)
    requires_acknowledgment = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        db_table = "documents_document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "project", "status"], name="docs_doc_org_proj_status_idx"),
            models.Index(fields=["organization", "folder"], name="docs_doc_org_folder_idx"),
            models.Index(fields=["organization", "is_current_version"], name="docs_doc_org_current_idx"),
            models.Index(fields=["project", "is_current_version"], name="docs_doc_proj_current_idx"),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"


class DocumentAcknowledgment(models.Model):
    """
    Records that a user has acknowledged/reviewed a document.

    Not a TenantModel — org accessible via Document FK.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="acknowledgments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_acknowledgments",
    )
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "documents_acknowledgment"
        verbose_name = "Document Acknowledgment"
        verbose_name_plural = "Document Acknowledgments"
        unique_together = [["document", "user"]]
        ordering = ["-acknowledged_at"]
        indexes = [
            models.Index(fields=["document", "user"], name="docs_ack_doc_user_idx"),
        ]

    def __str__(self):
        return f"{self.user} acknowledged {self.document}"


class RFI(TenantModel):
    """
    Request for Information — formal Q&A process for construction projects.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        ANSWERED = "ANSWERED", "Answered"
        CLOSED = "CLOSED", "Closed"

    class Priority(models.TextChoices):
        URGENT = "URGENT", "Urgent"
        HIGH = "HIGH", "High"
        NORMAL = "NORMAL", "Normal"
        LOW = "LOW", "Low"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="rfis",
    )
    rfi_number = models.IntegerField(
        help_text="Auto-incremented per project"
    )
    subject = models.CharField(max_length=300)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rfis_requested",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rfis_assigned",
    )
    cost_impact = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    schedule_impact_days = models.IntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    distribution_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="rfi_distributions",
        help_text="Users who receive RFI answer notifications",
    )

    class Meta:
        db_table = "documents_rfi"
        verbose_name = "RFI"
        verbose_name_plural = "RFIs"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "rfi_number"],
                name="unique_rfi_number_per_project",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "project", "status"], name="docs_rfi_org_proj_status_idx"),
            models.Index(fields=["organization", "project", "priority"], name="docs_rfi_org_proj_priority_idx"),
            models.Index(fields=["organization", "assigned_to"], name="docs_rfi_org_assigned_idx"),
            models.Index(fields=["project", "rfi_number"], name="docs_rfi_proj_number_idx"),
        ]

    def __str__(self):
        return f"RFI-{self.rfi_number:03d}: {self.subject}"


class Submittal(TenantModel):
    """
    Construction submittal — formal material/equipment approval workflow.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        APPROVED_AS_NOTED = "APPROVED_AS_NOTED", "Approved As Noted"
        REVISE_RESUBMIT = "REVISE_RESUBMIT", "Revise & Resubmit"
        REJECTED = "REJECTED", "Rejected"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="submittals",
    )
    submittal_number = models.IntegerField(
        help_text="Auto-incremented per project"
    )
    title = models.CharField(max_length=300)
    spec_section = models.CharField(
        max_length=100, blank=True, help_text="CSI specification section reference"
    )
    status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.DRAFT
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submittals_submitted",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submittals_reviewing",
    )
    due_date = models.DateField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name="submittals",
    )

    class Meta:
        db_table = "documents_submittal"
        verbose_name = "Submittal"
        verbose_name_plural = "Submittals"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "submittal_number"],
                name="unique_submittal_number_per_project",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "project", "status"], name="docs_submittal_org_proj_status_idx"),
            models.Index(fields=["organization", "reviewer"], name="docs_submittal_org_reviewer_idx"),
            models.Index(fields=["project", "submittal_number"], name="docs_submittal_proj_num_idx"),
        ]

    def __str__(self):
        return f"SUB-{self.submittal_number:03d}: {self.title}"


class Photo(TenantModel):
    """
    Project photo with EXIF metadata, GPS coordinates, and AI categorization.
    Thumbnails generated automatically on upload.
    """

    class Category(models.TextChoices):
        PROGRESS = "PROGRESS", "Progress"
        BEFORE = "BEFORE", "Before"
        AFTER = "AFTER", "After"
        DEFICIENCY = "DEFICIENCY", "Deficiency"
        DELIVERY = "DELIVERY", "Delivery"
        INSPECTION = "INSPECTION", "Inspection"
        SAFETY = "SAFETY", "Safety"
        OTHER = "OTHER", "Other"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="photos",
    )
    # S3 storage
    file_key = models.CharField(max_length=1000, help_text="S3 object key")
    thumbnail_key = models.CharField(
        max_length=1000, blank=True, help_text="S3 key for 400px thumbnail"
    )
    file_name = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True, default="image/jpeg")
    # Photo metadata
    caption = models.CharField(max_length=500, blank=True, null=True)
    taken_at = models.DateTimeField(
        null=True, blank=True, help_text="EXIF timestamp or upload time"
    )
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    phase = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Project phase when photo was taken"
    )
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.PROGRESS
    )
    ai_tags = models.JSONField(
        default=list, blank=True, help_text="Auto-generated AI categories"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_photos",
    )
    is_client_visible = models.BooleanField(default=True)
    linked_daily_log = models.ForeignKey(
        "field_ops.DailyLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photos",
    )
    annotations = models.JSONField(
        null=True,
        blank=True,
        help_text="Markup data: arrows, text, highlights (canvas overlay JSON)",
    )

    class Meta:
        db_table = "documents_photo"
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        ordering = ["-taken_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "project", "category"], name="docs_photo_org_proj_cat_idx"),
            models.Index(fields=["organization", "project", "-taken_at"], name="docs_photo_org_proj_taken_idx"),
            models.Index(fields=["organization", "is_client_visible"], name="docs_photo_org_visible_idx"),
            models.Index(fields=["project", "linked_daily_log"], name="docs_photo_proj_log_idx"),
        ]

    def __str__(self):
        return f"Photo: {self.file_name} ({self.project})"


class PhotoAlbum(TenantModel):
    """
    Curated or auto-generated collection of project photos.
    """

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="photo_albums",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_photo = models.ForeignKey(
        Photo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_for_albums",
    )
    is_auto_generated = models.BooleanField(
        default=False, help_text="AI-created album"
    )
    photos = models.ManyToManyField(
        Photo,
        blank=True,
        related_name="albums",
    )

    class Meta:
        db_table = "documents_photo_album"
        verbose_name = "Photo Album"
        verbose_name_plural = "Photo Albums"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "project"], name="docs_album_org_proj_idx"),
        ]

    def __str__(self):
        return f"Album: {self.name} — {self.project}"
