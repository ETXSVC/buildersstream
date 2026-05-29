"""
Migration 0002: Full Section 13 quality & safety models.

- Deletes scaffold: Inspection, SafetyIncident, SafetyChecklist
- Creates: InspectionChecklist, ChecklistItem, Inspection, InspectionResult,
           Deficiency, SafetyIncident, ToolboxTalk
"""
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality_safety', '0001_initial'),
        ('documents', '0001_initial'),   # Photo M2M
        ('projects', '0001_initial'),
        ('tenants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # 1. Remove old scaffold models
        # ------------------------------------------------------------------ #
        migrations.DeleteModel('Inspection'),
        migrations.DeleteModel('SafetyIncident'),
        migrations.DeleteModel('SafetyChecklist'),

        # ------------------------------------------------------------------ #
        # 2. InspectionChecklist (TenantModel)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='InspectionChecklist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('checklist_type', models.CharField(
                    max_length=20,
                    choices=[('quality', 'Quality'), ('safety', 'Safety'), ('regulatory', 'Regulatory')],
                    db_index=True,
                )),
                ('category', models.CharField(
                    max_length=20,
                    choices=[
                        ('framing', 'Framing'), ('electrical', 'Electrical'), ('plumbing', 'Plumbing'),
                        ('hvac', 'HVAC'), ('roofing', 'Roofing'), ('concrete', 'Concrete'),
                        ('final', 'Final'), ('safety_daily', 'Daily Safety'),
                        ('safety_weekly', 'Weekly Safety'), ('osha', 'OSHA Compliance'),
                    ],
                    db_index=True,
                )),
                ('description', models.TextField(blank=True)),
                ('is_template', models.BooleanField(default=True, db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
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
            options={'ordering': ['category', 'name'], 'abstract': False},
        ),
        migrations.AddIndex(
            model_name='inspectionchecklist',
            index=models.Index(fields=['organization', 'checklist_type'], name='qs_cl_org_type_idx'),
        ),
        migrations.AddIndex(
            model_name='inspectionchecklist',
            index=models.Index(fields=['organization', 'category'], name='qs_cl_org_cat_idx'),
        ),
        migrations.AddIndex(
            model_name='inspectionchecklist',
            index=models.Index(fields=['organization', 'is_template'], name='qs_cl_org_tmpl_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 3. ChecklistItem (plain model)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='ChecklistItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=500)),
                ('is_required', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('checklist', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='quality_safety.inspectionchecklist',
                )),
            ],
            options={'ordering': ['sort_order', 'id']},
        ),

        # ------------------------------------------------------------------ #
        # 4. Inspection (TenantModel, new full spec)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inspection_date', models.DateField(db_index=True)),
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'),
                        ('passed', 'Passed'), ('failed', 'Failed'), ('conditional', 'Conditional Pass'),
                    ],
                    default='scheduled',
                    db_index=True,
                )),
                ('overall_score', models.IntegerField(null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('checklist', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='inspections',
                    to='quality_safety.inspectionchecklist',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('inspector', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_inspections',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('photos', models.ManyToManyField(
                    blank=True,
                    related_name='inspection_photos',
                    to='documents.photo',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='qs_inspections',
                    to='projects.project',
                )),
            ],
            options={'ordering': ['-inspection_date'], 'abstract': False},
        ),
        migrations.AddIndex(
            model_name='inspection',
            index=models.Index(fields=['organization', 'status'], name='qs_insp_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='inspection',
            index=models.Index(fields=['organization', 'inspection_date'], name='qs_insp_org_date_idx'),
        ),
        migrations.AddIndex(
            model_name='inspection',
            index=models.Index(fields=['project', 'inspection_date'], name='qs_insp_proj_date_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 5. InspectionResult (plain model)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='InspectionResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(
                    max_length=15,
                    choices=[
                        ('pass', 'Pass'), ('fail', 'Fail'),
                        ('na', 'N/A'), ('not_inspected', 'Not Inspected'),
                    ],
                    default='not_inspected',
                )),
                ('notes', models.TextField(blank=True)),
                ('checklist_item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='results',
                    to='quality_safety.checklistitem',
                )),
                ('inspection', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='results',
                    to='quality_safety.inspection',
                )),
                ('photo', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='inspection_result_photos',
                    to='documents.photo',
                )),
            ],
            options={'ordering': ['checklist_item__sort_order']},
        ),
        migrations.AlterUniqueTogether(
            name='inspectionresult',
            unique_together={('inspection', 'checklist_item')},
        ),

        # ------------------------------------------------------------------ #
        # 6. Deficiency (TenantModel)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='Deficiency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('severity', models.CharField(
                    max_length=10,
                    choices=[
                        ('critical', 'Critical'), ('major', 'Major'),
                        ('minor', 'Minor'), ('cosmetic', 'Cosmetic'),
                    ],
                    db_index=True,
                )),
                ('status', models.CharField(
                    max_length=15,
                    choices=[
                        ('open', 'Open'), ('in_progress', 'In Progress'),
                        ('resolved', 'Resolved'), ('verified', 'Verified'),
                    ],
                    default='open',
                    db_index=True,
                )),
                ('due_date', models.DateField(null=True, blank=True)),
                ('resolved_date', models.DateField(null=True, blank=True)),
                ('resolution_notes', models.TextField(blank=True)),
                ('assigned_to', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_deficiencies',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('inspection', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='deficiencies',
                    to='quality_safety.inspection',
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('photos', models.ManyToManyField(
                    blank=True,
                    related_name='deficiency_photos',
                    to='documents.photo',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='deficiencies',
                    to='projects.project',
                )),
                ('resolved_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='resolved_deficiencies',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('verified_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='verified_deficiencies',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-created_at'], 'abstract': False},
        ),
        migrations.AddIndex(
            model_name='deficiency',
            index=models.Index(fields=['organization', 'status'], name='qs_def_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='deficiency',
            index=models.Index(fields=['organization', 'severity'], name='qs_def_org_severity_idx'),
        ),
        migrations.AddIndex(
            model_name='deficiency',
            index=models.Index(fields=['project', 'status'], name='qs_def_proj_status_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 7. SafetyIncident (TenantModel, new full spec)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='SafetyIncident',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('incident_date', models.DateTimeField(db_index=True)),
                ('incident_type', models.CharField(
                    max_length=20,
                    choices=[
                        ('injury', 'Injury'), ('near_miss', 'Near Miss'),
                        ('property_damage', 'Property Damage'), ('environmental', 'Environmental'),
                        ('fire', 'Fire'), ('fall', 'Fall'), ('struck_by', 'Struck By'),
                        ('caught_in', 'Caught In/Between'), ('electrical', 'Electrical'),
                    ],
                    db_index=True,
                )),
                ('severity', models.CharField(
                    max_length=15,
                    choices=[
                        ('first_aid', 'First Aid'), ('medical', 'Medical Treatment'),
                        ('lost_time', 'Lost Time'), ('fatality', 'Fatality'),
                    ],
                    db_index=True,
                )),
                ('description', models.TextField()),
                ('witnesses', models.JSONField(default=list, blank=True)),
                ('injured_person_name', models.CharField(max_length=200, blank=True)),
                ('root_cause', models.TextField(blank=True)),
                ('corrective_actions', models.TextField(blank=True)),
                ('osha_reportable', models.BooleanField(default=False, db_index=True)),
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('reported', 'Reported'), ('investigating', 'Investigating'),
                        ('corrective_action', 'Corrective Action'), ('closed', 'Closed'),
                    ],
                    default='reported',
                    db_index=True,
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('photos', models.ManyToManyField(
                    blank=True,
                    related_name='safety_incident_photos',
                    to='documents.photo',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='qs_safety_incidents',
                    to='projects.project',
                )),
                ('reported_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reported_safety_incidents',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-incident_date'], 'abstract': False},
        ),
        migrations.AddIndex(
            model_name='safetyincident',
            index=models.Index(fields=['organization', 'status'], name='qs_si_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='safetyincident',
            index=models.Index(fields=['organization', 'incident_date'], name='qs_si_org_date_idx'),
        ),
        migrations.AddIndex(
            model_name='safetyincident',
            index=models.Index(fields=['project', 'incident_date'], name='qs_si_proj_date_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 8. ToolboxTalk (TenantModel)
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='ToolboxTalk',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('presented_date', models.DateField(db_index=True)),
                ('sign_in_sheet', models.ImageField(null=True, blank=True, upload_to='toolbox_talks/%Y/%m/')),
                ('attendees', models.ManyToManyField(
                    blank=True,
                    related_name='toolbox_talk_attendances',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='%(app_label)s_%(class)s_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.organization',
                )),
                ('presented_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='presented_toolbox_talks',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='toolbox_talks',
                    to='projects.project',
                )),
            ],
            options={'ordering': ['-presented_date'], 'abstract': False},
        ),
        migrations.AddIndex(
            model_name='toolboxtalk',
            index=models.Index(fields=['organization', 'presented_date'], name='qs_tbt_org_date_idx'),
        ),
        migrations.AddIndex(
            model_name='toolboxtalk',
            index=models.Index(fields=['project', 'presented_date'], name='qs_tbt_proj_date_idx'),
        ),
    ]
