"""
Service & Warranty Management v2.

Drops the placeholder ServiceTicket and WarrantyItem tables and replaces them
with the full-spec schema:
  - ServiceTicket  (expanded: ticket_number, client FK, ticket_type, billing fields)
  - Warranty       (new: replaces WarrantyItem)
  - WarrantyClaim  (new)
  - ServiceAgreement (new)
"""
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0001_initial"),
        ("crm", "0001_initial"),
        ("financials", "0003_full_financial_suite"),
        ("projects", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # Drop old stubs
        # ------------------------------------------------------------------ #
        migrations.DeleteModel(name="WarrantyItem"),
        migrations.DeleteModel(name="ServiceTicket"),

        # ------------------------------------------------------------------ #
        # ServiceTicket (full spec)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="ServiceTicket",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ticket_number", models.CharField(blank=True, db_index=True, max_length=30)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("priority", models.CharField(
                    choices=[("emergency", "Emergency"), ("high", "High"), ("normal", "Normal"), ("low", "Low")],
                    default="normal",
                    max_length=20,
                )),
                ("status", models.CharField(
                    choices=[("new", "New"), ("assigned", "Assigned"), ("in_progress", "In Progress"), ("on_hold", "On Hold"), ("completed", "Completed"), ("closed", "Closed")],
                    default="new",
                    max_length=20,
                )),
                ("ticket_type", models.CharField(
                    choices=[("warranty", "Warranty"), ("service_call", "Service Call"), ("maintenance", "Scheduled Maintenance"), ("callback", "Callback"), ("emergency", "Emergency")],
                    default="service_call",
                    max_length=20,
                )),
                ("scheduled_date", models.DateTimeField(blank=True, null=True)),
                ("completed_date", models.DateTimeField(blank=True, null=True)),
                ("resolution", models.TextField(blank=True)),
                ("billable", models.BooleanField(default=True)),
                ("billing_type", models.CharField(
                    choices=[("time_and_material", "Time & Material"), ("flat_rate", "Flat Rate"), ("warranty_no_charge", "Warranty (No Charge)")],
                    default="time_and_material",
                    max_length=30,
                )),
                ("labor_hours", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("parts_cost", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total_cost", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("assigned_to", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="assigned_service_tickets",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("client", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="service_tickets",
                    to="crm.contact",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="%(app_label)s_%(class)s_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("invoice", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="service_tickets",
                    to="financials.invoice",
                )),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(app_label)s_%(class)s_set",
                    to="tenants.organization",
                )),
                ("project", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="service_tickets",
                    to="projects.project",
                )),
            ],
            options={"ordering": ["-created_at"], "abstract": False},
        ),
        migrations.AddIndex(
            model_name="serviceticket",
            index=models.Index(fields=["organization", "status"], name="svc_ticket_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceticket",
            index=models.Index(fields=["organization", "priority"], name="svc_ticket_org_priority_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceticket",
            index=models.Index(fields=["organization", "-created_at"], name="svc_ticket_org_created_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceticket",
            index=models.Index(fields=["assigned_to", "status"], name="svc_ticket_assignee_status_idx"),
        ),

        # ------------------------------------------------------------------ #
        # Warranty (replaces WarrantyItem)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Warranty",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("warranty_type", models.CharField(
                    choices=[("workmanship", "Workmanship"), ("manufacturer", "Manufacturer"), ("extended", "Extended")],
                    default="workmanship",
                    max_length=20,
                )),
                ("description", models.CharField(max_length=255)),
                ("coverage_details", models.TextField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("manufacturer", models.CharField(blank=True, max_length=255)),
                ("product_info", models.JSONField(blank=True, null=True)),
                ("status", models.CharField(
                    choices=[("active", "Active"), ("expired", "Expired"), ("claimed", "Claimed")],
                    default="active",
                    max_length=20,
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="%(app_label)s_%(class)s_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(app_label)s_%(class)s_set",
                    to="tenants.organization",
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="warranties",
                    to="projects.project",
                )),
            ],
            options={"ordering": ["end_date"], "abstract": False},
        ),
        migrations.AddIndex(
            model_name="warranty",
            index=models.Index(fields=["organization", "status"], name="svc_warranty_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="warranty",
            index=models.Index(fields=["organization", "end_date"], name="svc_warranty_org_end_idx"),
        ),
        migrations.AddIndex(
            model_name="warranty",
            index=models.Index(fields=["project", "warranty_type"], name="svc_warranty_proj_type_idx"),
        ),

        # ------------------------------------------------------------------ #
        # WarrantyClaim
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="WarrantyClaim",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("description", models.TextField()),
                ("status", models.CharField(
                    choices=[("filed", "Filed"), ("in_review", "In Review"), ("approved", "Approved"), ("denied", "Denied"), ("resolved", "Resolved")],
                    default="filed",
                    max_length=20,
                )),
                ("cost", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("resolution", models.TextField(blank=True)),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="%(app_label)s_%(class)s_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(app_label)s_%(class)s_set",
                    to="tenants.organization",
                )),
                ("service_ticket", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="warranty_claims",
                    to="service.serviceticket",
                )),
                ("warranty", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="claims",
                    to="service.warranty",
                )),
            ],
            options={"ordering": ["-created_at"], "abstract": False},
        ),
        migrations.AddIndex(
            model_name="warrantyclaim",
            index=models.Index(fields=["organization", "status"], name="svc_wclm_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="warrantyclaim",
            index=models.Index(fields=["warranty", "status"], name="svc_wclm_warranty_status_idx"),
        ),

        # ------------------------------------------------------------------ #
        # ServiceAgreement
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="ServiceAgreement",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("agreement_type", models.CharField(
                    choices=[("maintenance", "Maintenance"), ("inspection", "Inspection"), ("full_service", "Full Service")],
                    default="maintenance",
                    max_length=20,
                )),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("billing_frequency", models.CharField(
                    choices=[("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")],
                    default="monthly",
                    max_length=20,
                )),
                ("billing_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("visits_per_year", models.PositiveIntegerField(default=12)),
                ("visits_completed", models.PositiveIntegerField(default=0)),
                ("auto_renew", models.BooleanField(default=True)),
                ("status", models.CharField(
                    choices=[("active", "Active"), ("expired", "Expired"), ("canceled", "Canceled")],
                    default="active",
                    max_length=20,
                )),
                ("notes", models.TextField(blank=True)),
                ("client", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="service_agreements",
                    to="crm.contact",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="%(app_label)s_%(class)s_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(app_label)s_%(class)s_set",
                    to="tenants.organization",
                )),
            ],
            options={"ordering": ["end_date"], "abstract": False},
        ),
        migrations.AddIndex(
            model_name="serviceagreement",
            index=models.Index(fields=["organization", "status"], name="svc_agree_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceagreement",
            index=models.Index(fields=["organization", "end_date"], name="svc_agree_org_end_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceagreement",
            index=models.Index(fields=["client", "status"], name="svc_agree_client_status_idx"),
        ),
    ]
