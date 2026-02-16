# BuilderStream — Claude Code Instructions

Project-specific instructions for BuilderStream Django SaaS platform.

## Project Status

**Completed Sections:**
- ✅ Section 1: Scaffold (Django 5.x, DRF, multi-app structure)
- ✅ Section 2: Multi-Tenant Foundation (organizations, memberships, modules)
- ✅ Section 3: Authentication & User Management (email-only JWT, registration, password reset)
- ✅ Section 4: Billing Integration (Stripe subscriptions, webhooks, plan enforcement)
- ✅ Section 5: Project Command Center (lifecycle state machine, health scoring, dashboard)

**Remaining Sections:** CRM, Estimating, Scheduling, Financials, Client Portal, Documents, Field Ops, Quality & Safety, Payroll, Service & Warranty, Analytics

## Architecture Patterns

### Multi-Tenancy

**Pattern:** Row-level organization-based with thread-local isolation

**Key Components:**
- `TenantModel` — abstract base with `organization` FK and `TenantManager`
- `TenantManager` — `.for_organization(org)`, `.unscoped()` methods
- `TenantMiddleware` — resolves org context via `X-Organization-ID` header or user's last active org
- `TenantViewSetMixin` — auto-injects org filtering into ViewSets

**Thread-Local Context:**
```python
from apps.tenants.context import get_current_organization, set_current_organization, tenant_context

# In views/middleware (auto-set by TenantMiddleware)
org = get_current_organization()

# In Celery tasks (must manually set)
@shared_task
def my_task(org_id):
    from apps.tenants.models import Organization
    org = Organization.objects.get(pk=org_id)
    with tenant_context(org):
        # All TenantModel queries auto-scoped
        Project.objects.all()  # Only this org's projects
```

**CRITICAL:** Always use `.unscoped()` in Celery tasks that need cross-org access or explicit filtering.

### Authentication

**Pattern:** Email-only (no username), JWT tokens, email verification

**User Model:** `apps.accounts.User` — UUID pk, email-only login, `email_verified` flag
**Auth Method:** SimpleJWT with custom token serializer returning user profile + orgs
**Registration:** Atomic user + org + membership creation via signals

**Headers for authenticated requests:**
```http
Authorization: Bearer <access_token>
X-Organization-ID: <uuid>  # Required for tenant context
```

### Permissions

**Standard Classes:**
- `IsOrganizationMember` — any active member
- `IsOrganizationAdmin` — admin or owner
- `IsOrganizationOwner` — owner only
- `role_required('project_manager')` — factory function (hierarchical RBAC)
- `HasModuleAccess('module_key')` — feature gate for modules

**Role Hierarchy:** owner (7) > admin (6) > project_manager (5) > estimator (4) > accountant (3) > field_worker (2) > read_only (1)

### Billing

**Pattern:** Stripe subscriptions with usage-based metering and webhook processing

**Key Models:**
- `SubscriptionPlan` — Starter/Professional/Enterprise tiers with feature limits
- `UsageRecord` — monthly aggregation per metric (projects, users, documents, etc.)
- `Invoice` — Stripe invoice mirror with status tracking

**Subscription Flow:**
1. User creates org → signal auto-creates Stripe customer + Trial subscription
2. Trial conversion → `POST /api/v1/billing/subscribe/` with `price_id`
3. Stripe webhook confirms → subscription activated
4. Usage metering → Celery task aggregates monthly usage
5. Stripe webhook processes invoices → payment success/failure

**Middleware:** `SubscriptionRequiredMiddleware` blocks access if subscription is not `active` or `trialing`

### Project Lifecycle (Section 5)

**Pattern:** State machine with stage-gate requirements and health scoring

**10 Statuses:** LEAD → PROSPECT → ESTIMATE → PROPOSAL → CONTRACT → PRODUCTION → PUNCH_LIST → CLOSEOUT → COMPLETED (+ CANCELED from any)

**Stage-Gate Requirements:**
- **CONTRACT**: Must have `client_assigned` + `estimated_value_set`
- **PRODUCTION**: Must have `start_date_set` + `team_assigned`
- **COMPLETED**: Must have `actual_completion_set`

**Lifecycle Service:**
```python
from apps.projects.services import ProjectLifecycleService

# Transition with validation
ProjectLifecycleService.transition_status(
    project=project,
    new_status="production",
    user=request.user,
    notes="Starting construction phase",
)
# Raises ValueError if transition invalid or requirements not met

# Health scoring (0-100 + GREEN/YELLOW/RED)
score, status = ProjectLifecycleService.calculate_health_score(project)
# Budget variance (40pts) + schedule variance (30pts) + overdue items (30pts)
```

**Auto-Generated Project Numbers:** `BSP-{YEAR}-{SEQ:03d}` per org via `ProjectNumberService.generate_project_number(org)`

**Dashboard Caching:** Redis (db 1, 60s TTL) via `DashboardService.get_dashboard_data(org, user)`

**Celery Tasks:**
- `projects.calculate_all_health_scores` — hourly recalculation for active projects
- `projects.generate_action_items` — every 30min, auto-creates for overdue projects + upcoming milestones
- `projects.cache_dashboard_data` — on-demand cache warming

**Project Signals:**
- `pre_save` — caches old status for transition detection
- `post_save (created)` — logs creation activity + seeds 7 default milestones
- `post_save (status changed)` — logs status change activity

### API Endpoints (Section 5)

**Project Management:**
- `GET/POST /api/v1/projects/` — list/create (auto-generates project number)
- `GET/PUT/PATCH/DELETE /api/v1/projects/{pk}/` — detail operations
- `POST /api/v1/projects/{pk}/transition-status/` — lifecycle state machine
- `GET/POST/DELETE /api/v1/projects/{pk}/team-members/` — manage team
- `GET/POST /api/v1/projects/{pk}/milestones/` — manage milestones
- `GET /api/v1/projects/{pk}/activity/` — project activity log
- `GET /api/v1/projects/{pk}/transitions/` — transition audit trail

**Dashboard & Activity:**
- `GET /api/v1/dashboard/` — cached org dashboard (financial snapshot, schedule overview, action items, activity stream)
- `GET/PUT /api/v1/dashboard/layout/` — per-user widget layout (auto-creates on first access)
- `GET/POST/PUT/DELETE /api/v1/action-items/` — action items CRUD with org scoping
- `GET /api/v1/activity/` — org-wide activity stream (paginated, filterable)

## Docker Workflow

**IMPORTANT:** All Django management commands must run via Docker:

```bash
cd builderstream/  # Must be in directory with docker-compose.yml

# Migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Django shell
docker compose exec web python manage.py shell

# Tests
docker compose exec web pytest

# Create demo org
docker compose exec web python manage.py create_demo_org
```

## Database Migrations

**Pattern:** Manual migrations for complex schema changes

**When to write manual migrations:**
- Field renames (Django can't reliably detect)
- Data migrations (status/type enum changes, backfills)
- Adding non-nullable fields to existing tables
- Complex constraint changes

**Example from Section 5:**
```python
# 0002_expand_project_add_models.py
operations = [
    # 1. Rename fields first (preserves data)
    migrations.RenameField("Project", "number", "project_number"),

    # 2. Add new nullable fields
    migrations.AddField("Project", "client", ...),

    # 3. Data migration
    migrations.RunPython(migrate_project_status_and_type, reverse_code=...),

    # 4. Add constraints
    migrations.AlterField("Project", "project_number", unique=True),

    # 5. Create new models
    migrations.CreateModel("ProjectTeamMember", ...),
]
```

## Service Layer

**Pattern:** Complex business logic in service classes (not views or models)

**Examples:**
- `ProjectNumberService` — auto-incrementing project numbers per org per year
- `ProjectLifecycleService` — state machine with validation
- `DashboardService` — cached aggregation
- `StripeService` — Stripe API interactions
- `EmailService` — transactional email via SES/SMTP

**Why Services?**
- Keep views thin (coordination only)
- Keep models focused (data + simple computed properties)
- Testable business logic in isolation
- Reusable across views, tasks, management commands

## Celery Tasks

**Pattern:** Async operations via Redis broker (db 0), separate from Django cache (db 1)

**Task Naming:** `app_label.task_name` format for Celery beat schedule
**Task Decorator:** `@shared_task(name="projects.calculate_health_scores")`

**Common Patterns:**
```python
@shared_task(name="projects.my_task")
def my_task(organization_id):
    from apps.tenants.models import Organization
    from apps.tenants.context import tenant_context

    org = Organization.objects.get(pk=organization_id)
    with tenant_context(org):
        # All TenantModel queries auto-scoped
        projects = Project.objects.filter(is_active=True)
        for project in projects.iterator():  # Memory-efficient
            process(project)
```

**Celery Beat Schedule:** Defined in `config/settings/base.py` CELERY_BEAT_SCHEDULE
**Beat Scheduler:** `django_celery_beat.schedulers:DatabaseScheduler` (dynamic schedules via admin)

## Serializers

**Pattern:** Multiple serializers per model for different contexts

**Naming Convention:**
- `{Model}Serializer` — default/detail view
- `{Model}ListSerializer` — compact list view (read-only, fewer fields)
- `{Model}CreateSerializer` — creation-specific validation
- `{Model}UpdateSerializer` — update-specific validation (if needed)

**Example from Section 5:**
```python
class ProjectListSerializer(serializers.ModelSerializer):
    """Compact for list views."""
    client_name = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "status", "client_name", ...]
        read_only_fields = fields  # List is always read-only

class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full detail with nested relations."""
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        fields = [..., "team_members", "milestones", "custom_fields", ...]

class ProjectCreateSerializer(serializers.ModelSerializer):
    """Creation logic: auto-generate project_number."""
    def create(self, validated_data):
        org = self.context.get("organization")
        validated_data["project_number"] = ProjectNumberService.generate_project_number(org)
        return super().create(validated_data)
```

**ViewSet Pattern:**
```python
class ProjectViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        if self.action == "create":
            return ProjectCreateSerializer
        return ProjectDetailSerializer
```

## Signals

**Pattern:** Side effects (activity logging, defaults, cascades) via Django signals

**Project Signals (apps/projects/signals.py):**
```python
@receiver(pre_save, sender=Project)
def cache_old_status(sender, instance, **kwargs):
    """Cache previous status for change detection."""
    if instance.pk:
        old = Project.objects.unscoped().get(pk=instance.pk)
        instance._old_status = old.status

@receiver(post_save, sender=Project)
def on_project_save(sender, instance, created, **kwargs):
    if created:
        # Log activity + seed milestones
        ActivityLog.objects.create(...)
        ProjectMilestone.objects.bulk_create([...])
    else:
        # Detect status change
        if instance._old_status != instance.status:
            ActivityLog.objects.create(...)
```

**Signal Registration:** Add `ready()` method in `apps.py`:
```python
class ProjectsConfig(AppConfig):
    def ready(self):
        import apps.projects.signals  # noqa: F401
```

## Testing Strategy

**Pattern:** Pytest with fixtures, authenticated API client, tenant context

**Test Structure:**
```
apps/projects/tests/
├── conftest.py          # Fixtures (org, user, client)
├── test_models.py       # Model logic
├── test_services.py     # Business logic
├── test_views.py        # API endpoints
└── test_tasks.py        # Celery tasks
```

**Common Fixtures:**
```python
@pytest.fixture
def authenticated_client(user, org):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client.defaults["HTTP_X_ORGANIZATION_ID"] = str(org.id)
    return client
```

## Next Steps

To continue implementation, follow the master spec in `Documentation/builders_prompt.md`:
- Section 6: CRM & Pipeline (Contact model, deal stages, funnel)
- Section 7: Estimating & Takeoffs (cost database, line items, assemblies)
- Section 8: Scheduling & Crews (Gantt, resource allocation, availability)
- Section 9: Job Costing & Financials (budgets, actuals, change orders)
- Section 10: Client Portal (selections, approvals, communication)
- Section 11: Document Management (folders, RFIs, submittals, OCR)
- Section 12: Field Operations (daily logs, time tracking, expenses)
- Section 13: Quality & Safety (inspections, incidents, OSHA compliance)
- Section 14: Payroll (time sheets, pay periods, certified payroll)
- Section 15: Service & Warranty (tickets, maintenance, scheduling)
- Section 16: Analytics & Reporting (dashboards, custom reports, exports)

Each section follows the same pattern: models → services → serializers → views → URLs → signals/tasks → tests.
