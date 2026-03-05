"""Issue Tracking admin."""
from django.contrib import admin

from .models import CannedResponse, EscalationRule, Issue, IssueAttachment, IssueComment, IssueType


class IssueCommentInline(admin.TabularInline):
    model = IssueComment
    extra = 0
    readonly_fields = ["created_by", "created_at", "is_edited"]
    fields = ["content", "is_internal", "is_edited", "created_by", "created_at"]


class IssueAttachmentInline(admin.TabularInline):
    model = IssueAttachment
    extra = 0
    readonly_fields = ["uploaded_by", "created_at"]


@admin.register(IssueType)
class IssueTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "default_priority", "sla_response_hours", "sla_resolution_hours", "is_active"]
    list_filter = ["organization", "is_active", "default_priority"]
    search_fields = ["name"]


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ["number", "title", "organization", "status", "priority", "assignee", "sla_resolution_due_at"]
    list_filter = ["organization", "status", "priority", "issue_type"]
    search_fields = ["number", "title", "description"]
    readonly_fields = ["number", "sla_response_due_at", "sla_resolution_due_at", "first_responded_at", "resolved_at"]
    inlines = [IssueCommentInline, IssueAttachmentInline]


@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "issue_type", "is_active"]
    list_filter = ["organization", "issue_type", "is_active"]
    search_fields = ["name", "content"]


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "action_type", "is_active"]
    list_filter = ["organization", "action_type", "is_active"]
    search_fields = ["name"]
