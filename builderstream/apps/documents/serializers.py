"""
Document & Photo Control serializers.

Covers all 7 models with list/detail/create variants.
DocumentSerializer includes presigned download URL.
PhotoSerializer includes thumbnail URL.
"""

from rest_framework import serializers

from apps.documents.models import (
    Document,
    DocumentAcknowledgment,
    DocumentFolder,
    Photo,
    PhotoAlbum,
    RFI,
    Submittal,
)


# ---------------------------------------------------------------------------
# DocumentFolder
# ---------------------------------------------------------------------------

class DocumentFolderListSerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = [
            "id", "project", "name", "parent", "folder_type",
            "access_level", "sort_order", "children_count",
        ]
        read_only_fields = ["id"]

    def get_children_count(self, obj):
        return obj.children.count()


class DocumentFolderDetailSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = [
            "id", "project", "name", "parent", "folder_type",
            "access_level", "sort_order", "document_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_document_count(self, obj):
        return obj.documents.filter(is_current_version=True).count()


class DocumentFolderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFolder
        fields = ["project", "name", "parent", "folder_type", "access_level", "sort_order"]


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class DocumentListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    folder_name = serializers.CharField(source="folder.name", read_only=True, default=None)

    class Meta:
        model = Document
        fields = [
            "id", "folder", "folder_name", "project", "title", "file_name",
            "file_size", "content_type", "version", "is_current_version",
            "status", "tags", "uploaded_by", "uploaded_by_name",
            "requires_acknowledgment", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return None


class DocumentDetailSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    acknowledgment_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id", "folder", "project", "title", "description",
            "file_key", "file_name", "file_size", "content_type",
            "version", "is_current_version", "previous_version",
            "uploaded_by", "uploaded_by_name",
            "tags", "requires_acknowledgment", "status",
            "download_url", "acknowledgment_count",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "file_key", "version", "is_current_version",
            "previous_version", "created_at", "updated_at",
        ]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return None

    def get_download_url(self, obj):
        if not obj.file_key:
            return None
        try:
            from apps.documents.services import FileUploadService
            return FileUploadService.generate_download_url(obj.file_key, obj.file_name)
        except Exception:
            return None

    def get_acknowledgment_count(self, obj):
        return obj.acknowledgments.count()


class DocumentCreateSerializer(serializers.Serializer):
    """
    Used for the upload_complete action — creates a Document record after
    the file has been uploaded directly to S3 via presigned URL.
    """
    folder = serializers.UUIDField(required=False, allow_null=True)
    project = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField(max_length=300)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    file_key = serializers.CharField()
    file_name = serializers.CharField()
    file_size = serializers.IntegerField(min_value=0)
    content_type = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    requires_acknowledgment = serializers.BooleanField(required=False, default=False)


class PresignedUploadRequestSerializer(serializers.Serializer):
    """Request body for generate_upload_url action."""
    file_name = serializers.CharField()
    content_type = serializers.CharField()
    project = serializers.UUIDField(required=False, allow_null=True)


class DocumentAcknowledgmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentAcknowledgment
        fields = ["id", "document", "user", "user_name", "acknowledged_at"]
        read_only_fields = ["id", "acknowledged_at"]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


# ---------------------------------------------------------------------------
# RFI
# ---------------------------------------------------------------------------

class RFIListSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = RFI
        fields = [
            "id", "project", "rfi_number", "subject", "status", "priority",
            "requested_by", "requested_by_name", "assigned_to", "assigned_to_name",
            "due_date", "answered_at", "created_at",
        ]
        read_only_fields = ["id", "rfi_number", "created_at"]

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.email
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None


class RFIDetailSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    distribution_emails = serializers.SerializerMethodField()

    class Meta:
        model = RFI
        fields = [
            "id", "project", "rfi_number", "subject", "question", "answer",
            "status", "priority",
            "requested_by", "requested_by_name",
            "assigned_to", "assigned_to_name",
            "cost_impact", "schedule_impact_days",
            "due_date", "answered_at",
            "distribution_list", "distribution_emails",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "rfi_number", "answered_at", "created_at", "updated_at",
        ]

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.email
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None

    def get_distribution_emails(self, obj):
        return list(obj.distribution_list.values_list("email", flat=True))


class RFICreateSerializer(serializers.ModelSerializer):
    distribution_list = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False,
        queryset=__import__("django.conf", fromlist=["settings"]).settings.AUTH_USER_MODEL
        if False else [],  # resolved at runtime
        required=False,
    )

    class Meta:
        model = RFI
        fields = [
            "project", "subject", "question", "priority",
            "assigned_to", "due_date", "cost_impact",
            "schedule_impact_days", "distribution_list",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["distribution_list"].child_relation.queryset = User.objects.all()


class RFIAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField()
    cost_impact = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    schedule_impact_days = serializers.IntegerField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Submittal
# ---------------------------------------------------------------------------

class SubmittalListSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Submittal
        fields = [
            "id", "project", "submittal_number", "title", "spec_section",
            "status", "submitted_by", "submitted_by_name",
            "reviewer", "reviewer_name", "due_date", "reviewed_at",
        ]
        read_only_fields = ["id", "submittal_number"]

    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.get_full_name() or obj.submitted_by.email
        return None

    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.get_full_name() or obj.reviewer.email
        return None


class SubmittalDetailSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Submittal
        fields = [
            "id", "project", "submittal_number", "title", "spec_section",
            "status", "submitted_by", "submitted_by_name",
            "reviewer", "reviewer_name",
            "due_date", "reviewed_at", "review_notes",
            "documents", "document_count",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "submittal_number", "reviewed_at", "created_at", "updated_at",
        ]

    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.get_full_name() or obj.submitted_by.email
        return None

    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.get_full_name() or obj.reviewer.email
        return None

    def get_document_count(self, obj):
        return obj.documents.count()


class SubmittalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submittal
        fields = [
            "project", "title", "spec_section",
            "reviewer", "due_date", "documents",
        ]


class SubmittalReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        "APPROVED", "APPROVED_AS_NOTED", "REVISE_RESUBMIT", "REJECTED"
    ])
    review_notes = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

class PhotoListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            "id", "project", "file_name", "file_size", "content_type",
            "caption", "taken_at", "category", "phase",
            "is_client_visible", "ai_tags",
            "uploaded_by", "uploaded_by_name", "thumbnail_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_key:
            try:
                from apps.documents.services import FileUploadService
                return FileUploadService.generate_download_url(obj.thumbnail_key)
            except Exception:
                pass
        return None


class PhotoDetailSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            "id", "project", "file_key", "thumbnail_key",
            "file_name", "file_size", "content_type",
            "caption", "taken_at", "latitude", "longitude",
            "phase", "category", "ai_tags",
            "uploaded_by", "uploaded_by_name",
            "is_client_visible", "linked_daily_log",
            "annotations", "thumbnail_url", "download_url",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "file_key", "thumbnail_key", "ai_tags",
            "created_at", "updated_at",
        ]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_key:
            try:
                from apps.documents.services import FileUploadService
                return FileUploadService.generate_download_url(obj.thumbnail_key)
            except Exception:
                pass
        return None

    def get_download_url(self, obj):
        if obj.file_key:
            try:
                from apps.documents.services import FileUploadService
                return FileUploadService.generate_download_url(obj.file_key, obj.file_name)
            except Exception:
                pass
        return None


class PhotoCreateSerializer(serializers.Serializer):
    """Used for upload_complete — create Photo record after S3 upload."""
    project = serializers.UUIDField()
    file_key = serializers.CharField()
    thumbnail_key = serializers.CharField(required=False, allow_blank=True, default="")
    file_name = serializers.CharField()
    file_size = serializers.IntegerField(min_value=0)
    content_type = serializers.CharField(default="image/jpeg")
    caption = serializers.CharField(required=False, allow_blank=True, default="")
    category = serializers.ChoiceField(choices=Photo.Category.choices, default="PROGRESS")
    phase = serializers.CharField(required=False, allow_blank=True, default="")
    is_client_visible = serializers.BooleanField(default=True)
    taken_at = serializers.DateTimeField(required=False, allow_null=True)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)


class BulkPhotoUploadRequestSerializer(serializers.Serializer):
    """Request multiple presigned upload URLs at once."""
    project = serializers.UUIDField()
    files = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="List of {file_name, content_type}",
    )


class PhotoAnnotateSerializer(serializers.Serializer):
    """Save canvas annotation markup on a photo."""
    annotations = serializers.JSONField()


# ---------------------------------------------------------------------------
# PhotoAlbum
# ---------------------------------------------------------------------------

class PhotoAlbumListSerializer(serializers.ModelSerializer):
    photo_count = serializers.SerializerMethodField()
    cover_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = PhotoAlbum
        fields = [
            "id", "project", "name", "description",
            "is_auto_generated", "photo_count", "cover_thumbnail_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_photo_count(self, obj):
        return obj.photos.count()

    def get_cover_thumbnail_url(self, obj):
        if obj.cover_photo and obj.cover_photo.thumbnail_key:
            try:
                from apps.documents.services import FileUploadService
                return FileUploadService.generate_download_url(obj.cover_photo.thumbnail_key)
            except Exception:
                pass
        return None


class PhotoAlbumDetailSerializer(serializers.ModelSerializer):
    photos_data = PhotoListSerializer(source="photos", many=True, read_only=True)

    class Meta:
        model = PhotoAlbum
        fields = [
            "id", "project", "name", "description",
            "cover_photo", "is_auto_generated", "photos",
            "photos_data", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_auto_generated", "created_at", "updated_at"]


class PhotoAlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoAlbum
        fields = ["project", "name", "description", "cover_photo", "photos"]
