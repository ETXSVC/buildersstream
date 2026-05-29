"""Migration 0003: Replace stub models with full Financial Management Suite.

Drops the 3 stub tables (Budget OneToOne, Invoice simple, ChangeOrder simple)
and creates the complete schema: CostCode, Budget (line-item), Expense,
Invoice (full), InvoiceLineItem, Payment, ChangeOrder (full),
ChangeOrderLineItem, PurchaseOrder, PurchaseOrderLineItem.
"""
import decimal
import uuid

import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0001_initial"),
        ("financials", "0002_initial"),
        ("projects", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # 1. Drop old stub tables (order matters — FK deps first)             #
        # ------------------------------------------------------------------ #
        migrations.DeleteModel(name="Budget"),
        migrations.DeleteModel(name="Invoice"),
        migrations.DeleteModel(name="ChangeOrder"),

        # ------------------------------------------------------------------ #
        # 2. CostCode                                                         #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="CostCode",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_costcode_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="financials_costcode_created",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("code", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=200)),
                ("division", models.IntegerField(
                    choices=[
                        (1, "01 - General Conditions"),
                        (2, "02 - Existing Conditions"),
                        (3, "03 - Concrete"),
                        (4, "04 - Masonry"),
                        (5, "05 - Metals"),
                        (6, "06 - Wood, Plastics & Composites"),
                        (7, "07 - Thermal & Moisture Protection"),
                        (8, "08 - Openings"),
                        (9, "09 - Finishes"),
                        (10, "10 - Specialties"),
                        (11, "11 - Equipment"),
                        (12, "12 - Furnishings"),
                        (13, "13 - Special Construction"),
                        (14, "14 - Conveying Equipment"),
                        (22, "22 - Plumbing"),
                        (23, "23 - HVAC"),
                        (26, "26 - Electrical"),
                        (31, "31 - Earthwork"),
                        (32, "32 - Exterior Improvements"),
                        (33, "33 - Utilities"),
                    ],
                    default=1,
                )),
                ("category", models.CharField(max_length=100, blank=True)),
                ("is_labor", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AlterUniqueTogether(
            name="costcode",
            unique_together={("organization", "code")},
        ),
        migrations.AddIndex(
            model_name="costcode",
            index=models.Index(fields=["organization", "division"], name="fin_costcode_org_div_idx"),
        ),
        migrations.AddIndex(
            model_name="costcode",
            index=models.Index(fields=["organization", "is_active"], name="fin_costcode_org_active_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 3. Budget (line-item)                                               #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_budget_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="financials_budget_created",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="budget_lines",
                    to="projects.project",
                )),
                ("cost_code", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="budget_lines",
                    to="financials.costcode",
                )),
                ("description", models.CharField(max_length=200)),
                ("budget_type", models.CharField(
                    choices=[("original", "Original"), ("revised", "Revised")],
                    default="original",
                    max_length=20,
                )),
                ("budgeted_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("committed_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("actual_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("variance_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("variance_percent", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=7)),
                ("notes", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AddIndex(
            model_name="budget",
            index=models.Index(fields=["organization", "project"], name="fin_budget_org_proj_idx"),
        ),
        migrations.AddIndex(
            model_name="budget",
            index=models.Index(fields=["organization", "cost_code"], name="fin_budget_org_code_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 4. Expense                                                           #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_expense_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="financials_expense_created",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financial_expenses",
                    to="projects.project",
                )),
                ("cost_code", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="expenses",
                    to="financials.costcode",
                )),
                ("budget_line", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="expenses",
                    to="financials.budget",
                )),
                ("expense_type", models.CharField(
                    choices=[
                        ("material", "Material"), ("labor", "Labor"),
                        ("subcontractor", "Subcontractor"), ("equipment", "Equipment"),
                        ("overhead", "Overhead"), ("other", "Other"),
                    ],
                    default="other",
                    max_length=20,
                )),
                ("vendor_name", models.CharField(max_length=200, blank=True)),
                ("description", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("expense_date", models.DateField()),
                ("receipt_key", models.CharField(max_length=500, blank=True)),
                ("receipt_url", models.URLField(max_length=500, blank=True)),
                ("approval_status", models.CharField(
                    choices=[("pending", "Pending Review"), ("approved", "Approved"), ("rejected", "Rejected")],
                    default="pending",
                    max_length=20,
                )),
                ("approved_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="approved_expenses",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="submitted_expenses",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("notes", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["organization", "project"], name="fin_expense_org_proj_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["organization", "expense_date"], name="fin_expense_org_date_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["organization", "approval_status"], name="fin_expense_org_status_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 5. Invoice (full)                                                   #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_invoice_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_invoices",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="invoices",
                    to="projects.project",
                )),
                ("client", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="invoices",
                    to="crm.contact",
                )),
                ("invoice_number", models.CharField(max_length=50)),
                ("invoice_type", models.CharField(
                    choices=[
                        ("standard", "Standard Invoice"),
                        ("progress", "Progress Billing (AIA G702)"),
                        ("final", "Final Invoice"),
                        ("retainage", "Retainage Release"),
                        ("deposit", "Deposit Request"),
                    ],
                    default="standard",
                    max_length=20,
                )),
                ("status", models.CharField(
                    choices=[
                        ("draft", "Draft"), ("sent", "Sent"), ("viewed", "Viewed"),
                        ("partial", "Partially Paid"), ("paid", "Paid"),
                        ("overdue", "Overdue"), ("void", "Void"),
                    ],
                    default="draft",
                    max_length=20,
                )),
                ("public_token", models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)),
                ("subtotal", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("tax_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("retainage_percent", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
                ("retainage_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("amount_paid", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("balance_due", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("scheduled_value", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("work_completed_previous", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("work_completed_this_period", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("issue_date", models.DateField(blank=True, null=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("paid_date", models.DateField(blank=True, null=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("sent_to_email", models.EmailField(blank=True)),
                ("viewed_at", models.DateTimeField(blank=True, null=True)),
                ("view_count", models.PositiveIntegerField(default=0)),
                ("stripe_invoice_id", models.CharField(max_length=100, blank=True)),
                ("stripe_payment_intent_id", models.CharField(max_length=100, blank=True)),
                ("notes", models.TextField(blank=True)),
                ("terms", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["organization", "status"], name="fin_invoice_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["organization", "project"], name="fin_invoice_org_proj_idx"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["organization", "due_date"], name="fin_invoice_org_due_idx"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["public_token"], name="fin_invoice_token_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 6. InvoiceLineItem                                                  #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="InvoiceLineItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="line_items",
                    to="financials.invoice",
                )),
                ("cost_code", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="invoice_lines",
                    to="financials.costcode",
                )),
                ("description", models.CharField(max_length=200)),
                ("quantity", models.DecimalField(decimal_places=4, default=decimal.Decimal("1.0000"), max_digits=10)),
                ("unit", models.CharField(max_length=20, blank=True)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=14)),
                ("line_total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),

        # ------------------------------------------------------------------ #
        # 7. Payment                                                          #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_payment_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="financials_payment_created",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("invoice", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="payments",
                    to="financials.invoice",
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="payments",
                    to="projects.project",
                )),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("payment_date", models.DateField()),
                ("payment_method", models.CharField(
                    choices=[
                        ("check", "Check"), ("ach", "ACH / Bank Transfer"),
                        ("credit_card", "Credit Card"), ("wire", "Wire Transfer"),
                        ("cash", "Cash"), ("stripe", "Stripe"), ("other", "Other"),
                    ],
                    default="check",
                    max_length=20,
                )),
                ("reference_number", models.CharField(max_length=100, blank=True)),
                ("stripe_charge_id", models.CharField(max_length=100, blank=True)),
                ("notes", models.TextField(blank=True)),
                ("recorded_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="recorded_payments",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
            ],
            options={"abstract": False},
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["organization", "invoice"], name="fin_payment_org_inv_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["organization", "payment_date"], name="fin_payment_org_date_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 8. ChangeOrder (full)                                               #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="ChangeOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_changeorder_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_change_orders",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="change_orders",
                    to="projects.project",
                )),
                ("client", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="change_orders",
                    to="crm.contact",
                )),
                ("number", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(
                    choices=[
                        ("draft", "Draft"), ("submitted", "Submitted to Client"),
                        ("under_review", "Under Review"), ("approved", "Approved"),
                        ("rejected", "Rejected"), ("void", "Void"),
                    ],
                    default="draft",
                    max_length=20,
                )),
                ("cost_impact", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("schedule_impact_days", models.IntegerField(default=0)),
                ("submitted_date", models.DateField(blank=True, null=True)),
                ("approved_date", models.DateField(blank=True, null=True)),
                ("rejected_date", models.DateField(blank=True, null=True)),
                ("approved_by_name", models.CharField(max_length=200, blank=True)),
                ("reason", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AlterUniqueTogether(
            name="changeorder",
            unique_together={("project", "number")},
        ),
        migrations.AddIndex(
            model_name="changeorder",
            index=models.Index(fields=["organization", "project"], name="fin_co_org_proj_idx"),
        ),
        migrations.AddIndex(
            model_name="changeorder",
            index=models.Index(fields=["organization", "status"], name="fin_co_org_status_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 9. ChangeOrderLineItem                                              #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="ChangeOrderLineItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("change_order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="line_items",
                    to="financials.changeorder",
                )),
                ("cost_code", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="co_lines",
                    to="financials.costcode",
                )),
                ("description", models.CharField(max_length=200)),
                ("quantity", models.DecimalField(decimal_places=4, default=decimal.Decimal("1.0000"), max_digits=10)),
                ("unit", models.CharField(max_length=20, blank=True)),
                ("unit_cost", models.DecimalField(decimal_places=2, max_digits=14)),
                ("line_total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),

        # ------------------------------------------------------------------ #
        # 10. PurchaseOrder                                                   #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="financials_purchaseorder_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_purchase_orders",
                    to=django.conf.settings.AUTH_USER_MODEL,
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="purchase_orders",
                    to="projects.project",
                )),
                ("po_number", models.CharField(max_length=50)),
                ("vendor_name", models.CharField(max_length=200)),
                ("vendor_email", models.EmailField(blank=True)),
                ("vendor_phone", models.CharField(max_length=30, blank=True)),
                ("status", models.CharField(
                    choices=[
                        ("draft", "Draft"), ("sent", "Sent to Vendor"),
                        ("acknowledged", "Acknowledged"), ("partial", "Partially Received"),
                        ("received", "Fully Received"), ("closed", "Closed"),
                        ("canceled", "Canceled"),
                    ],
                    default="draft",
                    max_length=20,
                )),
                ("subtotal", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("issue_date", models.DateField(blank=True, null=True)),
                ("expected_delivery_date", models.DateField(blank=True, null=True)),
                ("actual_delivery_date", models.DateField(blank=True, null=True)),
                ("delivery_location", models.CharField(max_length=200, blank=True)),
                ("notes", models.TextField(blank=True)),
                ("terms", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(fields=["organization", "project"], name="fin_po_org_proj_idx"),
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(fields=["organization", "status"], name="fin_po_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(fields=["organization", "vendor_name"], name="fin_po_org_vendor_idx"),
        ),

        # ------------------------------------------------------------------ #
        # 11. PurchaseOrderLineItem                                           #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="PurchaseOrderLineItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("purchase_order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="line_items",
                    to="financials.purchaseorder",
                )),
                ("cost_code", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="po_lines",
                    to="financials.costcode",
                )),
                ("description", models.CharField(max_length=200)),
                ("quantity", models.DecimalField(decimal_places=4, max_digits=10)),
                ("unit", models.CharField(max_length=20, blank=True)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=14)),
                ("line_total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=14)),
                ("received_quantity", models.DecimalField(decimal_places=4, default=decimal.Decimal("0.0000"), max_digits=10)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
    ]
