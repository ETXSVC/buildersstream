# Generated migration for estimating app
# 9 models: CostCode, CostItem, Assembly, AssemblyItem,
#            Estimate, EstimateSection, EstimateLineItem,
#            Proposal, ProposalTemplate

import decimal
import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0001_initial'),
        ('projects', '0001_initial'),
        ('tenants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------
        # ProposalTemplate (no FKs to estimating models)
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='ProposalTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('header_text', models.TextField(blank=True)),
                ('footer_text', models.TextField(blank=True)),
                ('terms_and_conditions', models.TextField()),
                ('signature_instructions', models.TextField(blank=True)),
                ('is_default', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Proposal Template',
                'verbose_name_plural': 'Proposal Templates',
                'db_table': 'estimating_proposal_templates',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='proposaltemplate',
            index=models.Index(fields=['organization', 'is_default'], name='estimating_proposaltemplate_org_default'),
        ),

        # ------------------------------------------------------------------
        # CostCode
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='CostCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(db_index=True, max_length=10)),
                ('name', models.CharField(max_length=200)),
                ('division', models.IntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(49),
                    ]
                )),
                ('category', models.CharField(blank=True, max_length=100)),
                ('is_labor', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Cost Code',
                'verbose_name_plural': 'Cost Codes',
                'db_table': 'estimating_cost_codes',
                'ordering': ['division', 'code'],
            },
        ),
        migrations.AddIndex(
            model_name='costcode',
            index=models.Index(fields=['organization', 'division'], name='estimating_costcode_org_division'),
        ),
        migrations.AddIndex(
            model_name='costcode',
            index=models.Index(fields=['organization', 'code'], name='estimating_costcode_org_code'),
        ),
        migrations.AddIndex(
            model_name='costcode',
            index=models.Index(fields=['organization', 'is_active'], name='estimating_costcode_org_active'),
        ),
        migrations.AddConstraint(
            model_name='costcode',
            constraint=models.UniqueConstraint(
                fields=['organization', 'code'],
                name='unique_cost_code_per_org',
            ),
        ),

        # ------------------------------------------------------------------
        # CostItem
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='CostItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('unit', models.CharField(max_length=20)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=14)),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=14)),
                ('client_price', models.DecimalField(decimal_places=2, max_digits=14)),
                ('markup_percent', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=5)),
                ('labor_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('is_taxable', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('cost_code', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cost_items',
                    to='estimating.costcode',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Cost Item',
                'verbose_name_plural': 'Cost Items',
                'db_table': 'estimating_cost_items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='costitem',
            index=models.Index(fields=['organization', 'cost_code'], name='estimating_costitem_org_costcode'),
        ),
        migrations.AddIndex(
            model_name='costitem',
            index=models.Index(fields=['organization', '-created_at'], name='estimating_costitem_org_created'),
        ),
        migrations.AddIndex(
            model_name='costitem',
            index=models.Index(fields=['organization', 'is_active'], name='estimating_costitem_org_active'),
        ),

        # ------------------------------------------------------------------
        # Assembly
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('total_cost', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('total_price', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Assembly',
                'verbose_name_plural': 'Assemblies',
                'db_table': 'estimating_assemblies',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='assembly',
            index=models.Index(fields=['organization', '-created_at'], name='estimating_assembly_org_created'),
        ),
        migrations.AddIndex(
            model_name='assembly',
            index=models.Index(fields=['organization', 'is_active'], name='estimating_assembly_org_active'),
        ),

        # ------------------------------------------------------------------
        # AssemblyItem
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='AssemblyItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=10)),
                ('sort_order', models.IntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('assembly', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assembly_items',
                    to='estimating.assembly',
                )),
                ('cost_item', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='assembly_items',
                    to='estimating.costitem',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Assembly Item',
                'verbose_name_plural': 'Assembly Items',
                'db_table': 'estimating_assembly_items',
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddIndex(
            model_name='assemblyitem',
            index=models.Index(fields=['assembly', 'sort_order'], name='estimating_assemblyitem_assembly_order'),
        ),

        # ------------------------------------------------------------------
        # Estimate
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('estimate_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('in_review', 'In Review'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                        ('sent_to_client', 'Sent to Client'),
                    ],
                    default='draft',
                    max_length=30,
                )),
                ('subtotal', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('total', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('notes', models.TextField(blank=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='approved_estimates',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_estimates',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('lead', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='estimates',
                    to='crm.lead',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('project', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='estimates',
                    to='projects.project',
                )),
            ],
            options={
                'verbose_name': 'Estimate',
                'verbose_name_plural': 'Estimates',
                'db_table': 'estimating_estimates',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='estimate',
            index=models.Index(fields=['organization', 'status'], name='estimating_estimate_org_status'),
        ),
        migrations.AddIndex(
            model_name='estimate',
            index=models.Index(fields=['organization', 'project'], name='estimating_estimate_org_project'),
        ),
        migrations.AddIndex(
            model_name='estimate',
            index=models.Index(fields=['organization', 'lead'], name='estimating_estimate_org_lead'),
        ),
        migrations.AddIndex(
            model_name='estimate',
            index=models.Index(fields=['organization', '-created_at'], name='estimating_estimate_org_created'),
        ),

        # ------------------------------------------------------------------
        # EstimateSection
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='EstimateSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('subtotal', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('estimate', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sections',
                    to='estimating.estimate',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name': 'Estimate Section',
                'verbose_name_plural': 'Estimate Sections',
                'db_table': 'estimating_sections',
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddIndex(
            model_name='estimatesection',
            index=models.Index(fields=['estimate', 'sort_order'], name='estimating_section_estimate_order'),
        ),

        # ------------------------------------------------------------------
        # EstimateLineItem
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='EstimateLineItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=10)),
                ('unit', models.CharField(max_length=20)),
                ('unit_cost', models.DecimalField(decimal_places=2, max_digits=14)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=14)),
                ('line_total', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=14)),
                ('is_taxable', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('assembly', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='estimate_line_items',
                    to='estimating.assembly',
                )),
                ('cost_item', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='estimate_line_items',
                    to='estimating.costitem',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('section', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='line_items',
                    to='estimating.estimatesection',
                )),
            ],
            options={
                'verbose_name': 'Estimate Line Item',
                'verbose_name_plural': 'Estimate Line Items',
                'db_table': 'estimating_line_items',
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddIndex(
            model_name='estimatelineitem',
            index=models.Index(fields=['section', 'sort_order'], name='estimating_lineitem_section_order'),
        ),
        migrations.AddIndex(
            model_name='estimatelineitem',
            index=models.Index(fields=['cost_item'], name='estimating_lineitem_costitem'),
        ),
        migrations.AddIndex(
            model_name='estimatelineitem',
            index=models.Index(fields=['assembly'], name='estimating_lineitem_assembly'),
        ),
        migrations.AddConstraint(
            model_name='estimatelineitem',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(cost_item__isnull=False, assembly__isnull=True)
                    | models.Q(cost_item__isnull=True, assembly__isnull=False)
                ),
                name='estimating_line_item_either_cost_or_assembly',
            ),
        ),

        # ------------------------------------------------------------------
        # Proposal
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('proposal_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('public_token', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('sent', 'Sent'),
                        ('viewed', 'Viewed'),
                        ('signed', 'Signed'),
                        ('expired', 'Expired'),
                        ('rejected', 'Rejected'),
                    ],
                    default='draft',
                    max_length=30,
                )),
                ('pdf_file', models.FileField(blank=True, upload_to='proposals/%Y/%m/')),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('sent_to_email', models.EmailField(blank=True)),
                ('viewed_at', models.DateTimeField(blank=True, null=True)),
                ('view_count', models.IntegerField(default=0)),
                ('signed_at', models.DateTimeField(blank=True, null=True)),
                ('signed_by_name', models.CharField(blank=True, max_length=200)),
                ('signature_image', models.ImageField(blank=True, upload_to='signatures/%Y/%m/')),
                ('signature_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('signature_user_agent', models.TextField(blank=True)),
                ('is_signed', models.BooleanField(default=False)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('terms_and_conditions', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('client', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='proposals',
                    to='crm.contact',
                )),
                ('estimate', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='proposals',
                    to='estimating.estimate',
                )),
                ('lead', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proposals',
                    to='crm.lead',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('project', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proposals',
                    to='projects.project',
                )),
                ('template', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proposals',
                    to='estimating.proposaltemplate',
                )),
            ],
            options={
                'verbose_name': 'Proposal',
                'verbose_name_plural': 'Proposals',
                'db_table': 'estimating_proposals',
                'ordering': ['-sent_at', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['organization', 'status'], name='estimating_proposal_org_status'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['organization', 'client'], name='estimating_proposal_org_client'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['public_token'], name='estimating_proposal_token'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['organization', '-sent_at'], name='estimating_proposal_org_sent'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['organization', 'is_signed'], name='estimating_proposal_org_signed'),
        ),
    ]
