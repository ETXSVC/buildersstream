"""Migration: drop stub payroll tables and create full Section 14 schema."""
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0002_initial"),
        ("projects", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # Phase 1: Drop old stub tables (reverse order of FK dependencies)   #
        # ------------------------------------------------------------------ #
        migrations.DeleteModel("CertifiedPayroll"),
        migrations.DeleteModel("PayrollRecord"),
        migrations.DeleteModel("PayPeriod"),

        # ------------------------------------------------------------------ #
        # Phase 2: Create Employee                                            #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(class)ss",
                    to="tenants.organization",
                )),
                ("user", models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="employee_profile",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("employee_id", models.CharField(db_index=True, max_length=20)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("employment_type", models.CharField(
                    choices=[
                        ("w2_full_time", "W-2 Full Time"),
                        ("w2_part_time", "W-2 Part Time"),
                        ("1099_contractor", "1099 Contractor"),
                    ],
                    db_index=True, max_length=20,
                )),
                ("trade", models.CharField(
                    choices=[
                        ("general", "General"), ("framing", "Framing"),
                        ("electrical", "Electrical"), ("plumbing", "Plumbing"),
                        ("hvac", "HVAC"), ("painting", "Painting"),
                        ("flooring", "Flooring"), ("roofing", "Roofing"),
                        ("concrete", "Concrete"), ("drywall", "Drywall"),
                        ("finish_carpentry", "Finish Carpentry"), ("other", "Other"),
                    ],
                    db_index=True, max_length=20,
                )),
                ("hire_date", models.DateField()),
                ("termination_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("base_hourly_rate", models.DecimalField(decimal_places=2, max_digits=8)),
                ("overtime_rate_multiplier", models.DecimalField(decimal_places=2, default=Decimal("1.50"), max_digits=4)),
                ("burden_rate", models.DecimalField(decimal_places=4, default=Decimal("0.2800"), max_digits=5)),
                ("ssn_last_four", models.CharField(blank=True, max_length=4)),
                ("tax_filing_status", models.CharField(
                    choices=[
                        ("single", "Single"),
                        ("married_joint", "Married Filing Jointly"),
                        ("married_separate", "Married Filing Separately"),
                        ("head_of_household", "Head of Household"),
                    ],
                    default="single", max_length=25,
                )),
                ("federal_allowances", models.IntegerField(default=0)),
                ("state_allowances", models.IntegerField(default=0)),
                ("direct_deposit_accounts", models.JSONField(blank=True, default=list)),
                ("certifications", models.JSONField(blank=True, default=list)),
                ("emergency_contact", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.AlterUniqueTogether(
            name="employee",
            unique_together={("organization", "employee_id")},
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["organization", "trade"], name="payroll_emp_org_trade_idx"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["organization", "is_active"], name="payroll_emp_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["organization", "employment_type"], name="payroll_emp_org_type_idx"),
        ),

        # ------------------------------------------------------------------ #
        # Phase 3: Create PayrollRun                                          #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="PayrollRun",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(class)ss",
                    to="tenants.organization",
                )),
                ("pay_period_start", models.DateField(db_index=True)),
                ("pay_period_end", models.DateField(db_index=True)),
                ("run_date", models.DateField()),
                ("check_date", models.DateField()),
                ("status", models.CharField(
                    choices=[
                        ("draft", "Draft"), ("processing", "Processing"),
                        ("approved", "Approved"), ("paid", "Paid"), ("void", "Void"),
                    ],
                    db_index=True, default="draft", max_length=15,
                )),
                ("total_gross", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_taxes", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_deductions", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_net", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("approved_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="approved_payroll_runs",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
            ],
            options={"ordering": ["-pay_period_end"]},
        ),
        migrations.AddIndex(
            model_name="payrollrun",
            index=models.Index(fields=["organization", "status"], name="payroll_run_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="payrollrun",
            index=models.Index(fields=["organization", "pay_period_end"], name="payroll_run_org_end_idx"),
        ),

        # ------------------------------------------------------------------ #
        # Phase 4: Create PayrollEntry                                        #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="PayrollEntry",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("payroll_run", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="entries",
                    to="payroll.payrollrun",
                )),
                ("employee", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="payroll_entries",
                    to="payroll.employee",
                )),
                ("regular_hours", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                ("overtime_hours", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                ("double_time_hours", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                ("regular_rate", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=8)),
                ("gross_pay", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("federal_tax", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("state_tax", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("fica", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("medicare", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("deductions", models.JSONField(blank=True, default=list)),
                ("net_pay", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("job_cost_allocations", models.JSONField(blank=True, default=list)),
            ],
            options={"ordering": ["employee__last_name", "employee__first_name"]},
        ),
        migrations.AlterUniqueTogether(
            name="payrollentry",
            unique_together={("payroll_run", "employee")},
        ),

        # ------------------------------------------------------------------ #
        # Phase 5: Create CertifiedPayrollReport                             #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="CertifiedPayrollReport",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(class)ss",
                    to="tenants.organization",
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="certified_payroll_reports",
                    to="projects.project",
                )),
                ("payroll_run", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="certified_reports",
                    to="payroll.payrollrun",
                )),
                ("report_type", models.CharField(
                    choices=[("wh_347", "Federal WH-347"), ("state_specific", "State Specific")],
                    default="wh_347", max_length=20,
                )),
                ("week_ending", models.DateField(db_index=True)),
                ("status", models.CharField(
                    choices=[("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted")],
                    db_index=True, default="draft", max_length=15,
                )),
                ("generated_file_key", models.CharField(blank=True, max_length=500)),
                ("compliance_issues", models.JSONField(blank=True, default=list)),
            ],
            options={"ordering": ["-week_ending"]},
        ),
        migrations.AddIndex(
            model_name="certifiedpayrollreport",
            index=models.Index(fields=["organization", "status"], name="payroll_cpr_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="certifiedpayrollreport",
            index=models.Index(fields=["project", "week_ending"], name="payroll_cpr_proj_week_idx"),
        ),

        # ------------------------------------------------------------------ #
        # Phase 6: Create PrevailingWageRate                                  #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="PrevailingWageRate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(class)ss",
                    to="tenants.organization",
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="prevailing_wage_rates",
                    to="projects.project",
                )),
                ("trade", models.CharField(
                    choices=[
                        ("general", "General"), ("framing", "Framing"),
                        ("electrical", "Electrical"), ("plumbing", "Plumbing"),
                        ("hvac", "HVAC"), ("painting", "Painting"),
                        ("flooring", "Flooring"), ("roofing", "Roofing"),
                        ("concrete", "Concrete"), ("drywall", "Drywall"),
                        ("finish_carpentry", "Finish Carpentry"), ("other", "Other"),
                    ],
                    db_index=True, max_length=20,
                )),
                ("base_rate", models.DecimalField(decimal_places=2, max_digits=8)),
                ("fringe_rate", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=8)),
                ("total_rate", models.DecimalField(decimal_places=2, max_digits=8)),
                ("effective_date", models.DateField()),
            ],
            options={"ordering": ["-effective_date"]},
        ),
        migrations.AlterUniqueTogether(
            name="prevailingwagerate",
            unique_together={("project", "trade", "effective_date")},
        ),
        migrations.AddIndex(
            model_name="prevailingwagerate",
            index=models.Index(fields=["organization", "project"], name="payroll_pwr_org_proj_idx"),
        ),
    ]
