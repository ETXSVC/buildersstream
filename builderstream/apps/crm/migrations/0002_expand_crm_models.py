# Manual migration for Section 6: CRM & Lead Management
# Expands Contact/PipelineStage, renames Deal→Lead, adds Company/Interaction/AutomationRule/EmailTemplate

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


def migrate_contact_data(apps, schema_editor):
    """Update ContactType choices and source data."""
    Contact = apps.get_model("crm", "Contact")

    # Map old contact_type values to new ones
    # Old: lead, prospect, client, subcontractor, vendor
    # New: lead, client, subcontractor, vendor, architect, other
    # "prospect" → "lead" (closest match)
    Contact.objects.filter(contact_type="prospect").update(contact_type="lead")


def reverse_contact_data(apps, schema_editor):
    """Reverse contact data migration."""
    pass  # Cannot reverse uniquely


def migrate_deal_to_lead(apps, schema_editor):
    """Copy Deal field data for Lead transition (title→description, notes preserved)."""
    # Rename will preserve data, but we need to combine title and notes into description
    db_alias = schema_editor.connection.alias

    # Use raw SQL to combine title and notes into description
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            UPDATE crm_deal
            SET notes = CASE
                WHEN notes = '' THEN title
                WHEN title = '' THEN notes
                ELSE title || E'\\n\\n' || notes
            END
        """)


def reverse_deal_to_lead(apps, schema_editor):
    """Reverse lead data migration."""
    pass  # Cannot reverse uniquely


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('projects', '0003_rename_projects_ai_org_resolved_idx_projects_ac_organiz_c100fb_idx_and_more'),
    ]

    operations = [
        # ===== Phase 1: Contact expansion =====

        # Rename company → company_name for backward compatibility
        migrations.RenameField(
            model_name='contact',
            old_name='company',
            new_name='company_name',
        ),

        # Add new Contact fields (all nullable for backward compatibility)
        migrations.AddField(
            model_name='contact',
            name='mobile_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='job_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='address_line1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='address_line2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='state',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='lead_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='contact',
            name='custom_fields',
            field=models.JSONField(blank=True, default=dict),
        ),

        # Update ContactType choices (add ARCHITECT, OTHER; remove PROSPECT via data migration)
        migrations.AlterField(
            model_name='contact',
            name='contact_type',
            field=models.CharField(
                choices=[
                    ('lead', 'Lead'),
                    ('client', 'Client'),
                    ('subcontractor', 'Subcontractor'),
                    ('vendor', 'Vendor'),
                    ('architect', 'Architect'),
                    ('other', 'Other'),
                ],
                default='lead',
                max_length=20,
            ),
        ),

        # Convert source to proper Choice field
        migrations.AlterField(
            model_name='contact',
            name='source',
            field=models.CharField(
                blank=True,
                choices=[
                    ('website_form', 'Website Form'),
                    ('phone', 'Phone Call'),
                    ('email', 'Email'),
                    ('referral', 'Referral'),
                    ('home_advisor', 'HomeAdvisor'),
                    ('angi', "Angi (Angie's List)"),
                    ('houzz', 'Houzz'),
                    ('home_show', 'Home Show'),
                    ('social_media', 'Social Media'),
                    ('walk_in', 'Walk-In'),
                    ('other', 'Other'),
                ],
                max_length=20,
            ),
        ),

        # Run Contact data migration (prospect→lead)
        migrations.RunPython(migrate_contact_data, reverse_contact_data),

        # ===== Phase 2: PipelineStage expansion =====

        # Rename order → sort_order
        migrations.RenameField(
            model_name='pipelinestage',
            old_name='order',
            new_name='sort_order',
        ),

        # Add new PipelineStage fields
        migrations.AddField(
            model_name='pipelinestage',
            name='is_won_stage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pipelinestage',
            name='is_lost_stage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pipelinestage',
            name='auto_actions',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Automatic actions triggered when lead enters this stage',
            ),
        ),

        # Update PipelineStage Meta
        migrations.AlterModelOptions(
            name='pipelinestage',
            options={'ordering': ['sort_order']},
        ),

        # ===== Phase 3: Deal → Lead rename and expansion =====

        # Prepare data: combine title and notes into description (notes field)
        migrations.RunPython(migrate_deal_to_lead, reverse_deal_to_lead),

        # Rename table from crm_deal to crm_lead
        migrations.AlterModelTable(
            name='deal',
            table='crm_lead',
        ),

        # Rename stage FK → pipeline_stage FK
        migrations.RenameField(
            model_name='deal',
            old_name='stage',
            new_name='pipeline_stage',
        ),

        # Rename value → estimated_value
        migrations.RenameField(
            model_name='deal',
            old_name='value',
            new_name='estimated_value',
        ),

        # Rename expected_close → estimated_start
        migrations.RenameField(
            model_name='deal',
            old_name='expected_close',
            new_name='estimated_start',
        ),

        # Rename notes → description
        migrations.RenameField(
            model_name='deal',
            old_name='notes',
            new_name='description',
        ),

        # Remove title field (data already migrated to description)
        migrations.RemoveField(
            model_name='deal',
            name='title',
        ),

        # Remove probability field (not needed in Lead model)
        migrations.RemoveField(
            model_name='deal',
            name='probability',
        ),

        # Add new Lead fields
        migrations.AddField(
            model_name='deal',
            name='project_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('custom_home', 'Custom Home'),
                    ('residential_remodel', 'Residential Remodel'),
                    ('kitchen_bath', 'Kitchen & Bath'),
                    ('addition', 'Addition'),
                    ('commercial', 'Commercial'),
                    ('tenant_improvement', 'Tenant Improvement'),
                    ('roofing', 'Roofing'),
                    ('siding', 'Siding'),
                    ('other', 'Other'),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='deal',
            name='urgency',
            field=models.CharField(
                choices=[
                    ('hot', 'Hot - Immediate'),
                    ('warm', 'Warm - 1-3 Months'),
                    ('cold', 'Cold - 3+ Months'),
                ],
                default='warm',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='deal',
            name='lost_reason',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='deal',
            name='lost_to_competitor',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='deal',
            name='last_contacted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deal',
            name='next_follow_up',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deal',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='deal',
            name='converted_project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='source_lead',
                to='projects.project',
            ),
        ),

        # Rename model Deal → Lead
        migrations.RenameModel(
            old_name='Deal',
            new_name='Lead',
        ),

        # Update Lead Meta
        migrations.AlterModelOptions(
            name='lead',
            options={'ordering': ['-created_at']},
        ),

        # ===== Phase 4: Create Company model =====

        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('website', models.URLField(blank=True)),
                ('address_line1', models.CharField(blank=True, max_length=255)),
                ('address_line2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=2)),
                ('zip_code', models.CharField(blank=True, max_length=10)),
                ('company_type', models.CharField(
                    choices=[
                        ('client_company', 'Client Company'),
                        ('subcontractor', 'Subcontractor'),
                        ('vendor', 'Vendor'),
                        ('supplier', 'Supplier'),
                        ('architect_firm', 'Architect Firm'),
                    ],
                    default='client_company',
                    max_length=20,
                )),
                ('insurance_expiry', models.DateField(blank=True, null=True)),
                ('license_number', models.CharField(blank=True, max_length=100)),
                ('license_expiry', models.DateField(blank=True, null=True)),
                ('performance_rating', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Rating from 1.00 to 5.00',
                    max_digits=3,
                    null=True,
                )),
                ('notes', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'verbose_name_plural': 'Companies',
                'ordering': ['name'],
            },
        ),

        # Add Company FK to Contact (nullable)
        migrations.AddField(
            model_name='contact',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contacts',
                to='crm.company',
            ),
        ),

        # Add referred_by FK to Contact (self-referencing, nullable)
        migrations.AddField(
            model_name='contact',
            name='referred_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referrals',
                to='crm.contact',
            ),
        ),

        # ===== Phase 5: Create Interaction model =====

        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('interaction_type', models.CharField(
                    choices=[
                        ('email', 'Email'),
                        ('phone_call', 'Phone Call'),
                        ('sms', 'SMS/Text Message'),
                        ('site_visit', 'Site Visit'),
                        ('meeting', 'Meeting'),
                        ('note', 'Note'),
                    ],
                    max_length=20,
                )),
                ('direction', models.CharField(
                    choices=[
                        ('inbound', 'Inbound'),
                        ('outbound', 'Outbound'),
                    ],
                    default='outbound',
                    max_length=10,
                )),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('body', models.TextField()),
                ('occurred_at', models.DateTimeField()),
                ('contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interactions',
                    to='crm.contact',
                )),
                ('lead', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interactions',
                    to='crm.lead',
                )),
                ('logged_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='logged_interactions',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'ordering': ['-occurred_at'],
            },
        ),

        # ===== Phase 6: Create AutomationRule model =====

        migrations.CreateModel(
            name='AutomationRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('trigger_type', models.CharField(
                    choices=[
                        ('stage_change', 'Stage Change'),
                        ('time_delay', 'Time Delay (Inactivity)'),
                        ('lead_score_change', 'Lead Score Change'),
                        ('no_activity', 'No Activity Period'),
                    ],
                    max_length=20,
                )),
                ('trigger_config', models.JSONField(
                    default=dict,
                    help_text='Example: {"stage_id": "uuid"} or {"days_inactive": 7}',
                )),
                ('action_type', models.CharField(
                    choices=[
                        ('send_email', 'Send Email'),
                        ('send_sms', 'Send SMS'),
                        ('create_task', 'Create Task'),
                        ('assign_lead', 'Assign Lead'),
                        ('change_stage', 'Change Stage'),
                        ('notify_user', 'Notify User'),
                    ],
                    max_length=20,
                )),
                ('action_config', models.JSONField(
                    default=dict,
                    help_text='Example: {"template_id": "uuid", "assign_to_id": "uuid"}',
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),

        # ===== Phase 7: Create EmailTemplate model =====

        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('template_type', models.CharField(
                    choices=[
                        ('follow_up', 'Follow-Up'),
                        ('thank_you', 'Thank You'),
                        ('estimate_reminder', 'Estimate Reminder'),
                        ('review_request', 'Review Request'),
                        ('marketing', 'Marketing'),
                    ],
                    max_length=20,
                )),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField(
                    help_text='Supports variables: {{first_name}}, {{last_name}}, {{project_type}}, {{company_name}}, {{estimated_value}}',
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),

        # ===== Phase 8: Add indexes =====

        # Contact indexes
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['organization', 'contact_type'], name='crm_contact_org_type_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['organization', '-lead_score'], name='crm_contact_org_score_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['organization', '-created_at'], name='crm_contact_org_created_idx'),
        ),

        # Lead indexes
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['organization', 'pipeline_stage'], name='crm_lead_org_stage_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['organization', 'assigned_to'], name='crm_lead_org_assigned_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['organization', '-last_contacted_at'], name='crm_lead_org_contacted_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['organization', 'next_follow_up'], name='crm_lead_org_followup_idx'),
        ),

        # Interaction indexes
        migrations.AddIndex(
            model_name='interaction',
            index=models.Index(fields=['organization', 'contact', '-occurred_at'], name='crm_interact_org_contact_idx'),
        ),
        migrations.AddIndex(
            model_name='interaction',
            index=models.Index(fields=['organization', 'lead', '-occurred_at'], name='crm_interact_org_lead_idx'),
        ),
    ]
