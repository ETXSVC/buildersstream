"""Document admin configuration."""
from django.contrib import admin

from .models import Document, Folder, RFI, Submittal


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "parent"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "folder", "file_type", "version"]
    list_filter = ["file_type"]
    search_fields = ["title"]


@admin.register(RFI)
class RFIAdmin(admin.ModelAdmin):
    list_display = ["number", "subject", "project", "status", "due_date"]
    list_filter = ["status"]


@admin.register(Submittal)
class SubmittalAdmin(admin.ModelAdmin):
    list_display = ["number", "title", "project", "status", "required_date"]
    list_filter = ["status"]
