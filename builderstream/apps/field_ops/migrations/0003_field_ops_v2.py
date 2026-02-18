"""
Migration 0003: Full Section 12 field operations models.

- Replaces minimal DailyLog scaffold with full spec (log_date, status, weather_conditions,
  work_performed, delay_reason, visitors JSON, material_deliveries JSON, safety_incidents,
  approved_by, approved_at, photos M2M)
- Replaces minimal TimeEntry with full clock in/out spec (clock_in/out, status, GPS, overtime)
- Deletes old Expense scaffold; creates new ExpenseEntry model
- Creates DailyLogCrewEntry model
"""
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_ops', '0002_initial'),
        ('documents', '0001_initial'),   # for DailyLog.photos M2M
        ('financials', '0003_full_financial_suite'),  # for CostCode FK
        ('tenants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # 1. Evolve DailyLog
        # ------------------------------------------------------------------ #

        # Rename old text fields before adding JSON replacements
        migrations.RenameField('dailylog', 'date', 'log_date'),
        migrations.RenameField('dailylog', 'work_summary', 'work_performed'),
        migrations.RenameField('dailylog', 'issues', 'issues_encountered'),

        # Remove old scaffold-only fields
        migrations.RemoveField('dailylog', 'weather'),
        migrations.RemoveField('dailylog', 'temperature_high'),
        migrations.RemoveField('dailylog', 'temperature_low'),
        migrations.RemoveField('dailylog', 'workers_on_site'),

        # Add new fields
        migrations.AddField(
            model_name='dailylog',
            name='submitted_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='submitted_daily_logs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved')],
                default='draft',
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='weather_conditions',
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='delay_reason',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('weather', 'Weather'), ('material', 'Material Delay'),
                    ('labor', 'Labor Shortage'), ('inspection', 'Inspection'),
                    ('client', 'Client Decision'), ('permit', 'Permit Issue'),
                    ('equipment', 'Equipment Failure'), ('none', 'No Delay'),
                ],
                default='none',
            ),
        ),
        # Replace visitors TextField with JSONField
        migrations.RemoveField('dailylog', 'visitors'),
        migrations.AddField(
            model_name='dailylog',
            name='visitors',
            field=models.JSONField(default=list, blank=True),
        ),
        # Replace delays TextField with new delays TextField (nullable)
        migrations.AlterField(
            model_name='dailylog',
            name='delays',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='material_deliveries',
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='safety_incidents',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='approved_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_daily_logs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='dailylog',
            name='approved_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # M2M to documents.Photo (distinct name to avoid clash with linked_daily_log FK)
        migrations.AddField(
            model_name='dailylog',
            name='attached_photos',
            field=models.ManyToManyField(
                blank=True,
                related_name='daily_log_attachments',
                to='documents.photo',
            ),
        ),

        # Update unique_together after rename
        migrations.AlterUniqueTogether(
            name='dailylog',
            unique_together={('project', 'log_date')},
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='dailylog',
            index=models.Index(fields=['organization', 'log_date'], name='fops_log_org_date_idx'),
        ),
        migrations.AddIndex(
            model_name='dailylog',
            index=models.Index(fields=['organization', 'status'], name='fops_log_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='dailylog',
            index=models.Index(fields=['project', 'log_date'], name='fops_log_proj_date_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 2. Create DailyLogCrewEntry
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='DailyLogCrewEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('crew_or_trade', models.CharField(max_length=100)),
                ('worker_count', models.PositiveIntegerField(default=1)),
                ('hours_worked', models.DecimalField(decimal_places=2, max_digits=6)),
                ('work_description', models.TextField(blank=True)),
                ('daily_log', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='crew_entries',
                    to='field_ops.dailylog',
                )),
            ],
            options={
                'verbose_name_plural': 'Daily log crew entries',
                'ordering': ['crew_or_trade'],
            },
        ),

        # ------------------------------------------------------------------ #
        # 3. Evolve TimeEntry
        # ------------------------------------------------------------------ #

        # Remove old entry_type (REGULAR/OVERTIME/DOUBLE_TIME choices)
        migrations.RemoveField('timeentry', 'entry_type'),

        # Remove old is_approved boolean
        migrations.RemoveField('timeentry', 'is_approved'),

        # Rename description → notes
        migrations.RenameField('timeentry', 'description', 'notes'),

        # Change cost_code FK from estimating.CostCode to financials.CostCode
        migrations.RemoveField('timeentry', 'cost_code'),
        migrations.AddField(
            model_name='timeentry',
            name='cost_code',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='time_entries',
                to='financials.costcode',
            ),
        ),

        # Add new TimeEntry fields
        migrations.AddField(
            model_name='timeentry',
            name='entry_type',
            field=models.CharField(
                max_length=10,
                choices=[('clock', 'Clock In/Out'), ('manual', 'Manual Entry')],
                default='clock',
            ),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='status',
            field=models.CharField(
                max_length=10,
                choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='clock_in',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='clock_out',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='gps_clock_in',
            field=models.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='gps_clock_out',
            field=models.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='is_within_geofence',
            field=models.BooleanField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='overtime_hours',
            field=models.DecimalField(
                decimal_places=2, max_digits=6, default=Decimal('0.00'),
            ),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='approved_at',
            field=models.DateTimeField(null=True, blank=True),
        ),

        # Make hours default 0.00 instead of required
        migrations.AlterField(
            model_name='timeentry',
            name='hours',
            field=models.DecimalField(
                decimal_places=2, max_digits=6, default=Decimal('0.00'),
                help_text='Calculated from clock_in/out or entered manually.',
            ),
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='timeentry',
            index=models.Index(fields=['organization', 'user', 'date'], name='fops_te_org_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='timeentry',
            index=models.Index(fields=['organization', 'status'], name='fops_te_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='timeentry',
            index=models.Index(fields=['project', 'date'], name='fops_te_proj_date_idx'),
        ),

        # ------------------------------------------------------------------ #
        # 4. Delete old Expense model; create ExpenseEntry
        # ------------------------------------------------------------------ #
        migrations.DeleteModel('Expense'),

        migrations.CreateModel(
            name='ExpenseEntry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('category', models.CharField(
                    max_length=20,
                    choices=[
                        ('material', 'Material'), ('fuel', 'Fuel'), ('meals', 'Meals'),
                        ('tools', 'Tools'), ('equipment_rental', 'Equipment Rental'),
                        ('supplies', 'Supplies'), ('mileage', 'Mileage'), ('other', 'Other'),
                    ],
                    default='other',
                    db_index=True,
                )),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt_file_key', models.CharField(max_length=500, blank=True)),
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('pending', 'Pending'), ('approved', 'Approved'),
                        ('rejected', 'Rejected'), ('reimbursed', 'Reimbursed'),
                    ],
                    default='pending',
                    db_index=True,
                )),
                ('mileage', models.DecimalField(
                    decimal_places=2, max_digits=8, null=True, blank=True,
                    help_text='Miles driven (when category is MILEAGE).',
                )),
                ('approved_at', models.DateTimeField(null=True, blank=True)),
                ('approved_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='approved_expense_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('cost_code', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='expense_entries',
                    to='financials.costcode',
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
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='expense_entries',
                    to='projects.project',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='expense_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-date'], 'verbose_name_plural': 'expense entries'},
        ),

        # Indexes for ExpenseEntry
        migrations.AddIndex(
            model_name='expenseentry',
            index=models.Index(
                fields=['organization', 'user', 'date'], name='fops_exp_org_user_date_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='expenseentry',
            index=models.Index(fields=['organization', 'status'], name='fops_exp_org_status_idx'),
        ),
        migrations.AddIndex(
            model_name='expenseentry',
            index=models.Index(fields=['project', 'date'], name='fops_exp_proj_date_idx'),
        ),
    ]
