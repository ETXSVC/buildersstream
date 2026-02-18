"""Quality & Safety Compliance models."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class InspectionChecklist(TenantModel):
    """Inspection checklist template (reusable across projects)."""

    class ChecklistType(models.TextChoices):
        QUALITY = "quality", "Quality"
        SAFETY = "safety", "Safety"
        REGULATORY = "regulatory", "Regulatory"

    class Category(models.TextChoices):
        FRAMING = "framing", "Framing"
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        HVAC = "hvac", "HVAC"
        ROOFING = "roofing", "Roofing"
        CONCRETE = "concrete", "Concrete"
        FINAL = "final", "Final"
        SAFETY_DAILY = "safety_daily", "Daily Safety"
        SAFETY_WEEKLY = "safety_weekly", "Weekly Safety"
        OSHA = "osha", "OSHA Compliance"

    name = models.CharField(max_length=200)
    checklist_type = models.CharField(
        max_length=20, choices=ChecklistType.choices, db_index=True,
    )
    category = models.CharField(
        max_length=20, choices=Category.choices, db_index=True,
    )
    description = models.TextField(blank=True)
    is_template = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["organization", "checklist_type"], name="qs_cl_org_type_idx"),
            models.Index(fields=["organization", "category"], name="qs_cl_org_cat_idx"),
            models.Index(fields=["organization", "is_template"], name="qs_cl_org_tmpl_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ChecklistItem(models.Model):
    """Individual item within an inspection checklist.
    NOT a TenantModel — org accessible via checklist FK.
    """

    checklist = models.ForeignKey(
        InspectionChecklist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.CharField(max_length=500)
    is_required = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.description[:80]


class Inspection(TenantModel):
    """Inspection instance tied to a project and checklist."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        CONDITIONAL = "conditional", "Conditional Pass"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="qs_inspections",
    )
    checklist = models.ForeignKey(
        InspectionChecklist,
        on_delete=models.PROTECT,
        related_name="inspections",
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_inspections",
    )
    inspection_date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )
    overall_score = models.IntegerField(
        null=True, blank=True,
        help_text="0-100 score calculated from results.",
    )
    notes = models.TextField(blank=True)
    photos = models.ManyToManyField(
        "documents.Photo",
        blank=True,
        related_name="inspection_photos",
    )

    class Meta:
        ordering = ["-inspection_date"]
        indexes = [
            models.Index(fields=["organization", "status"], name="qs_insp_org_status_idx"),
            models.Index(fields=["organization", "inspection_date"], name="qs_insp_org_date_idx"),
            models.Index(fields=["project", "inspection_date"], name="qs_insp_proj_date_idx"),
        ]

    def __str__(self):
        return f"{self.checklist.name} – {self.inspection_date} ({self.get_status_display()})"


class InspectionResult(models.Model):
    """Per-item result within an inspection.
    NOT a TenantModel — org accessible via inspection FK.
    """

    class Status(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        NA = "na", "N/A"
        NOT_INSPECTED = "not_inspected", "Not Inspected"

    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name="results",
    )
    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name="results",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.NOT_INSPECTED,
    )
    notes = models.TextField(blank=True)
    photo = models.ForeignKey(
        "documents.Photo",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="inspection_result_photos",
    )

    class Meta:
        unique_together = [("inspection", "checklist_item")]
        ordering = ["checklist_item__sort_order"]

    def __str__(self):
        return f"{self.checklist_item}: {self.get_status_display()}"


class Deficiency(TenantModel):
    """Quality deficiency / punch-list item requiring corrective action."""

    class Severity(models.TextChoices):
        CRITICAL = "critical", "Critical"
        MAJOR = "major", "Major"
        MINOR = "minor", "Minor"
        COSMETIC = "cosmetic", "Cosmetic"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        VERIFIED = "verified", "Verified"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="deficiencies",
    )
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="deficiencies",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices, db_index=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_deficiencies",
    )
    due_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="resolved_deficiencies",
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="verified_deficiencies",
    )
    resolution_notes = models.TextField(blank=True)
    photos = models.ManyToManyField(
        "documents.Photo",
        blank=True,
        related_name="deficiency_photos",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"], name="qs_def_org_status_idx"),
            models.Index(fields=["organization", "severity"], name="qs_def_org_severity_idx"),
            models.Index(fields=["project", "status"], name="qs_def_proj_status_idx"),
        ]

    def __str__(self):
        return f"{self.title} [{self.get_severity_display()} – {self.get_status_display()}]"


class SafetyIncident(TenantModel):
    """Safety incident report (injury, near-miss, property damage, etc.)."""

    class IncidentType(models.TextChoices):
        INJURY = "injury", "Injury"
        NEAR_MISS = "near_miss", "Near Miss"
        PROPERTY_DAMAGE = "property_damage", "Property Damage"
        ENVIRONMENTAL = "environmental", "Environmental"
        FIRE = "fire", "Fire"
        FALL = "fall", "Fall"
        STRUCK_BY = "struck_by", "Struck By"
        CAUGHT_IN = "caught_in", "Caught In/Between"
        ELECTRICAL = "electrical", "Electrical"

    class Severity(models.TextChoices):
        FIRST_AID = "first_aid", "First Aid"
        MEDICAL = "medical", "Medical Treatment"
        LOST_TIME = "lost_time", "Lost Time"
        FATALITY = "fatality", "Fatality"

    class IncidentStatus(models.TextChoices):
        REPORTED = "reported", "Reported"
        INVESTIGATING = "investigating", "Investigating"
        CORRECTIVE_ACTION = "corrective_action", "Corrective Action"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="qs_safety_incidents",
    )
    incident_date = models.DateTimeField(db_index=True)
    incident_type = models.CharField(
        max_length=20, choices=IncidentType.choices, db_index=True,
    )
    severity = models.CharField(
        max_length=15, choices=Severity.choices, db_index=True,
    )
    description = models.TextField()
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reported_safety_incidents",
    )
    witnesses = models.JSONField(default=list, blank=True)
    injured_person_name = models.CharField(max_length=200, blank=True)
    root_cause = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    osha_reportable = models.BooleanField(default=False, db_index=True)
    photos = models.ManyToManyField(
        "documents.Photo",
        blank=True,
        related_name="safety_incident_photos",
    )
    status = models.CharField(
        max_length=20,
        choices=IncidentStatus.choices,
        default=IncidentStatus.REPORTED,
        db_index=True,
    )

    class Meta:
        ordering = ["-incident_date"]
        indexes = [
            models.Index(fields=["organization", "status"], name="qs_si_org_status_idx"),
            models.Index(fields=["organization", "incident_date"], name="qs_si_org_date_idx"),
            models.Index(fields=["project", "incident_date"], name="qs_si_proj_date_idx"),
        ]

    def __str__(self):
        return (
            f"{self.get_incident_type_display()} – "
            f"{self.incident_date.date()} ({self.get_severity_display()})"
        )


class ToolboxTalk(TenantModel):
    """Toolbox talk / safety meeting record."""

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="toolbox_talks",
    )
    topic = models.CharField(max_length=255)
    content = models.TextField()
    presented_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="presented_toolbox_talks",
    )
    presented_date = models.DateField(db_index=True)
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="toolbox_talk_attendances",
    )
    sign_in_sheet = models.ImageField(
        upload_to="toolbox_talks/%Y/%m/",
        null=True, blank=True,
    )

    class Meta:
        ordering = ["-presented_date"]
        indexes = [
            models.Index(fields=["organization", "presented_date"], name="qs_tbt_org_date_idx"),
            models.Index(fields=["project", "presented_date"], name="qs_tbt_proj_date_idx"),
        ]

    def __str__(self):
        return f"{self.topic} – {self.presented_date}"
