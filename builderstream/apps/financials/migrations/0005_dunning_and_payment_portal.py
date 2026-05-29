"""Add DunningRule, DunningEvent models and payment portal fields to Invoice."""
import uuid
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financials", "0004_add_currency_field"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        # Add payment portal fields to Invoice
        migrations.AddField(
            model_name="invoice",
            name="payment_due_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="payment_terms",
            field=models.CharField(blank=True, default="Net 30", max_length=100),
        ),
        migrations.AddField(
            model_name="invoice",
            name="allow_partial_payment",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="invoice",
            name="minimum_payment_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        # DunningRule model
        migrations.CreateModel(
            name="DunningRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("days_past_due", models.PositiveIntegerField()),
                ("action_type", models.CharField(
                    choices=[
                        ("email_reminder", "Send Email Reminder"),
                        ("suspend_portal", "Suspend Client Portal Access"),
                        ("flag_escalation", "Flag for Manual Escalation"),
                    ],
                    max_length=30,
                )),
                ("email_subject", models.CharField(blank=True, max_length=255)),
                ("email_body", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_dunningrule_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to="accounts.user",
                )),
            ],
            options={"ordering": ["days_past_due"]},
        ),
        migrations.AddIndex(
            model_name="dunningrule",
            index=models.Index(fields=["organization", "is_active"], name="fin_dunning_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="dunningrule",
            index=models.Index(fields=["organization", "days_past_due"], name="fin_dunning_org_days_idx"),
        ),
        # DunningEvent model
        migrations.CreateModel(
            name="DunningEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("triggered_at", models.DateTimeField(auto_now_add=True)),
                ("action_taken", models.CharField(max_length=30)),
                ("success", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True)),
                ("invoice", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="dunning_events",
                    to="financials.invoice",
                )),
                ("rule", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="events",
                    to="financials.dunningrule",
                )),
            ],
            options={"ordering": ["-triggered_at"]},
        ),
    ]
