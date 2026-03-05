"""Issue Tracking serializers."""
from django.utils import timezone
from rest_framework import serializers

from .models import CannedResponse, EscalationRule, Issue, IssueAttachment, IssueComment, IssueType


class IssueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueType
        fields = [
            "id", "name", "description", "icon", "color",
            "default_priority", "sla_response_hours", "sla_resolution_hours",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IssueListSerializer(serializers.ModelSerializer):
    assignee_name = serializers.SerializerMethodField()
    issue_type_name = serializers.SerializerMethodField()
    is_sla_response_breached = serializers.BooleanField(read_only=True)
    is_sla_resolution_breached = serializers.BooleanField(read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id", "number", "title", "priority", "status",
            "issue_type", "issue_type_name",
            "assignee", "assignee_name",
            "project", "client",
            "sla_response_due_at", "sla_resolution_due_at",
            "sla_response_met", "sla_resolution_met",
            "is_sla_response_breached", "is_sla_resolution_breached",
            "tags", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_assignee_name(self, obj):
        if obj.assignee:
            return f"{obj.assignee.first_name} {obj.assignee.last_name}".strip()
        return None

    def get_issue_type_name(self, obj):
        return obj.issue_type.name if obj.issue_type else None


class IssueCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = IssueComment
        fields = [
            "id", "issue", "parent", "content", "is_edited", "edited_at",
            "is_internal", "author_name", "replies", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_edited", "edited_at", "created_at", "updated_at"]

    def get_author_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_replies(self, obj):
        if obj.parent_id is None:
            # Only top-level comments get inline replies
            qs = obj.replies.order_by("created_at")
            return IssueCommentSerializer(qs, many=True).data
        return []


class IssueAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueAttachment
        fields = [
            "id", "issue", "filename", "file_size", "content_type",
            "file_key", "uploaded_by", "created_at",
        ]
        read_only_fields = ["id", "created_at", "uploaded_by"]


class IssueDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    attachments = IssueAttachmentSerializer(many=True, read_only=True)
    assignee_name = serializers.SerializerMethodField()
    reporter_name = serializers.SerializerMethodField()
    issue_type_detail = IssueTypeSerializer(source="issue_type", read_only=True)
    is_sla_response_breached = serializers.BooleanField(read_only=True)
    is_sla_resolution_breached = serializers.BooleanField(read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id", "number", "title", "description",
            "issue_type", "issue_type_detail",
            "priority", "status",
            "project", "client",
            "assignee", "assignee_name",
            "reporter", "reporter_name",
            "sla_response_due_at", "sla_resolution_due_at",
            "sla_response_met", "sla_resolution_met",
            "first_responded_at", "resolved_at",
            "is_sla_response_breached", "is_sla_resolution_breached",
            "tags", "custom_fields",
            "comments", "attachments",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "number", "sla_response_due_at", "sla_resolution_due_at",
            "sla_response_met", "sla_resolution_met",
            "first_responded_at", "resolved_at",
            "created_at", "updated_at",
        ]

    def get_comments(self, obj):
        top_level = obj.comments.filter(parent__isnull=True).order_by("created_at")
        return IssueCommentSerializer(top_level, many=True).data

    def get_assignee_name(self, obj):
        if obj.assignee:
            return f"{obj.assignee.first_name} {obj.assignee.last_name}".strip()
        return None

    def get_reporter_name(self, obj):
        if obj.reporter:
            return f"{obj.reporter.first_name} {obj.reporter.last_name}".strip()
        return None


class IssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "title", "description", "issue_type", "priority",
            "project", "client", "assignee", "tags", "custom_fields",
        ]

    def create(self, validated_data):
        from .services import IssueNumberService, SLAService

        org = self.context.get("organization")
        user = self.context["request"].user

        validated_data["organization"] = org
        validated_data["number"] = IssueNumberService.generate(org)
        validated_data["reporter"] = user

        issue = Issue(**validated_data)
        SLAService.calculate_due_dates(issue)
        issue.save()
        return issue


class CannedResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CannedResponse
        fields = ["id", "name", "content", "issue_type", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class EscalationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationRule
        fields = [
            "id", "name", "trigger_condition", "action_type",
            "action_config", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SLAComplianceSerializer(serializers.Serializer):
    total_issues = serializers.IntegerField()
    response_sla = serializers.DictField()
    resolution_sla = serializers.DictField()
    by_status = serializers.DictField()
    by_priority = serializers.DictField()
