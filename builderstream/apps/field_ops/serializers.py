"""Field operations serializers."""
from rest_framework import serializers

from .models import DailyLog, DailyLogCrewEntry, ExpenseEntry, TimeEntry


# ---------------------------------------------------------------------------
# DailyLog
# ---------------------------------------------------------------------------

class DailyLogCrewEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLogCrewEntry
        fields = ["id", "crew_or_trade", "worker_count", "hours_worked", "work_description"]


class DailyLogListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    submitted_by_name = serializers.SerializerMethodField()
    total_crew_hours = serializers.SerializerMethodField()

    class Meta:
        model = DailyLog
        fields = [
            "id", "project", "project_name", "log_date", "status",
            "submitted_by", "submitted_by_name", "safety_incidents",
            "delay_reason", "total_crew_hours", "created_at",
        ]

    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip()
        return None

    def get_total_crew_hours(self, obj):
        total = sum(e.hours_worked for e in obj.crew_entries.all())
        return float(total)


class DailyLogDetailSerializer(serializers.ModelSerializer):
    crew_entries = DailyLogCrewEntrySerializer(many=True, read_only=True)
    submitted_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = DailyLog
        fields = [
            "id", "organization", "project", "log_date", "status",
            "submitted_by", "submitted_by_name",
            "weather_conditions", "work_performed", "issues_encountered",
            "delays", "delay_reason",
            "visitors", "material_deliveries", "safety_incidents",
            "approved_by", "approved_by_name", "approved_at",
            "crew_entries", "photo_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "approved_by", "approved_at", "created_at", "updated_at"]

    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip()
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None

    def get_photo_count(self, obj):
        return obj.attached_photos.count()


class DailyLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = [
            "project", "log_date", "weather_conditions", "work_performed",
            "issues_encountered", "delays", "delay_reason",
            "visitors", "material_deliveries", "safety_incidents",
        ]


# ---------------------------------------------------------------------------
# TimeEntry
# ---------------------------------------------------------------------------

class TimeEntryListSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source="project.name", read_only=True)
    cost_code_display = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = [
            "id", "user", "user_name", "project", "project_name",
            "date", "clock_in", "clock_out", "hours", "overtime_hours",
            "entry_type", "status", "cost_code", "cost_code_display",
            "is_within_geofence", "created_at",
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_cost_code_display(self, obj):
        if obj.cost_code:
            return f"{obj.cost_code.code} — {obj.cost_code.name}"
        return None


class TimeEntryDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source="project.name", read_only=True)
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = [
            "id", "organization", "user", "user_name", "project", "project_name",
            "cost_code", "date", "clock_in", "clock_out", "hours", "overtime_hours",
            "entry_type", "status",
            "gps_clock_in", "gps_clock_out", "is_within_geofence",
            "notes", "approved_by", "approved_by_name", "approved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "hours", "overtime_hours", "approved_at", "created_at", "updated_at"]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """For manual time entries (not clock in/out)."""

    class Meta:
        model = TimeEntry
        fields = [
            "project", "date", "hours", "cost_code", "notes",
        ]

    def validate_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Hours must be positive.")
        return value


class ClockInSerializer(serializers.Serializer):
    project = serializers.UUIDField()
    gps_data = serializers.DictField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class ClockOutSerializer(serializers.Serializer):
    gps_data = serializers.DictField(required=False, allow_null=True)


class BulkApproveSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)
    action = serializers.ChoiceField(choices=["approve", "reject"], default="approve")


# ---------------------------------------------------------------------------
# ExpenseEntry
# ---------------------------------------------------------------------------

class ExpenseEntryListSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source="project.name", read_only=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseEntry
        fields = [
            "id", "user", "user_name", "project", "project_name",
            "date", "category", "description", "amount", "status",
            "mileage", "receipt_url", "created_at",
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_receipt_url(self, obj):
        if not obj.receipt_file_key:
            return None
        try:
            import boto3
            from django.conf import settings
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj.receipt_file_key},
                ExpiresIn=3600,
            )
        except Exception:
            return None


class ExpenseEntryDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source="project.name", read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseEntry
        fields = [
            "id", "organization", "user", "user_name", "project", "project_name",
            "cost_code", "date", "category", "description", "amount",
            "receipt_file_key", "receipt_url", "status", "mileage",
            "approved_by", "approved_by_name", "approved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "approved_at", "created_at", "updated_at"]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None

    def get_receipt_url(self, obj):
        if not obj.receipt_file_key:
            return None
        try:
            import boto3
            from django.conf import settings
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj.receipt_file_key},
                ExpiresIn=3600,
            )
        except Exception:
            return None


class ExpenseEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseEntry
        fields = [
            "project", "date", "category", "description", "amount",
            "cost_code", "mileage",
        ]

    def validate(self, attrs):
        if attrs.get("category") == ExpenseEntry.Category.MILEAGE and not attrs.get("mileage"):
            raise serializers.ValidationError(
                {"mileage": "Mileage is required when category is MILEAGE."}
            )
        return attrs
