"""Document & Photo Control admin configuration."""
from django.contrib import admin

from apps.documents.models import (
    Document,
    DocumentAcknowledgment,
    DocumentFolder,
    Photo,
    PhotoAlbum,
    RFI,
    Submittal,
)


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "project", "parent", "folder_type", "access_level", "sort_order"]
    list_filter = ["folder_type", "access_level"]
    search_fields = ["name"]
    raw_id_fields = ["project", "parent"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title", "organization", "project", "folder", "version",
        "is_current_version", "status", "file_size", "uploaded_by", "created_at",
    ]
    list_filter = ["status", "is_current_version", "requires_acknowledgment"]
    search_fields = ["title", "file_name", "file_key"]
    raw_id_fields = ["folder", "project", "uploaded_by", "previous_version"]
    readonly_fields = ["version", "is_current_version", "file_key", "created_at", "updated_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project", "folder", "uploaded_by")


@admin.register(DocumentAcknowledgment)
class DocumentAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = ["document", "user", "acknowledged_at"]
    raw_id_fields = ["document", "user"]
    readonly_fields = ["acknowledged_at"]


@admin.register(RFI)
class RFIAdmin(admin.ModelAdmin):
    list_display = [
        "rfi_number", "subject", "organization", "project",
        "status", "priority", "assigned_to", "due_date", "answered_at",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["subject", "question"]
    raw_id_fields = ["project", "requested_by", "assigned_to"]
    readonly_fields = ["rfi_number", "answered_at", "created_at", "updated_at"]
    filter_horizontal = ["distribution_list"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project", "assigned_to")


@admin.register(Submittal)
class SubmittalAdmin(admin.ModelAdmin):
    list_display = [
        "submittal_number", "title", "organization", "project",
        "status", "reviewer", "due_date", "reviewed_at",
    ]
    list_filter = ["status"]
    search_fields = ["title", "spec_section"]
    raw_id_fields = ["project", "submitted_by", "reviewer"]
    readonly_fields = ["submittal_number", "reviewed_at", "created_at", "updated_at"]
    filter_horizontal = ["documents"]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = [
        "file_name", "organization", "project", "category",
        "is_client_visible", "uploaded_by", "taken_at", "created_at",
    ]
    list_filter = ["category", "is_client_visible"]
    search_fields = ["file_name", "caption", "phase"]
    raw_id_fields = ["project", "uploaded_by", "linked_daily_log"]
    readonly_fields = ["file_key", "thumbnail_key", "ai_tags", "created_at", "updated_at"]


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "project", "is_auto_generated", "created_at"]
    list_filter = ["is_auto_generated"]
    search_fields = ["name", "description"]
    raw_id_fields = ["project", "cover_photo"]
    filter_horizontal = ["photos"]
