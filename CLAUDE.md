# BuilderStream - Claude Code Project Guide

## Project Overview
BuilderStream is a multi-tenant construction management SaaS built with Django 5.2.x, DRF, PostgreSQL 16, Redis 7, Celery, and React 18.

**Master Spec**: `Documentation/builders_prompt.md` (phased build guide — follow section by section)

## Quick Start
```bash
cd builderstream
docker compose up -d          # Start all services
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_demo_org
```

## Architecture

### Stack
- **Backend**: Django 5.2.x + Django REST Framework + Celery + Redis
- **Frontend**: React 18 (in `builderstream/frontend/`)
- **Database**: PostgreSQL 16 with UUID primary keys
- **Auth**: JWT via SimpleJWT, email-only (no username)
- **Multi-tenancy**: Row-level isolation via thread-local storage (not schema-based)
- **Billing**: Stripe subscriptions with per-seat pricing

### App Structure (16 apps)
```
builderstream/apps/
  core/         # Base models (TimeStampedModel, TenantModel), permissions
  tenants/      # Organization, Membership, ActiveModule, middleware, context
  accounts/     # User model, JWT auth, registration, invitations
  billing/      # Stripe billing, plans, webhooks, subscription enforcement
  projects/     # Project Command Center: lifecycle, health, dashboard, action items, activity
  crm/          # CRM & Lead Management: 7 models, pipeline, scoring, automation, analytics
  estimating/   # Cost estimation (scaffold)
  scheduling/   # Project scheduling (scaffold)
  financials/   # Financial management (scaffold)
  clients/      # Client portal (scaffold)
  documents/    # Document management (scaffold)
  field_ops/    # Field operations (scaffold)
  quality_safety/ # Quality & safety (scaffold)
  payroll/      # Payroll management (scaffold)
  service/      # Service & warranty (scaffold)
  analytics/    # Analytics & reporting (scaffold)
```

### Key Patterns
- **Base models**: `TimeStampedModel` (UUID PK, timestamps), `TenantModel` (+ org FK with auto-filtering)
- **TenantManager**: Auto-filters querysets via `get_current_organization()` thread-local
- **TenantMiddleware**: Resolves org from `X-Organization-ID` header > `last_active_organization` > first membership
- **SubscriptionRequiredMiddleware**: Enforces subscription status (active/trialing=full, past_due=read-only, canceled=402)
- **Permissions**: `IsOrganizationMember/Admin/Owner`, `role_required(min_role)`, `HasModuleAccess(key)`
- **Signals**: post_save(Organization) creates OWNER membership, default modules, Stripe customer
- **Plan config**: Constants in `billing/plans.py` (not a DB model) — TRIAL, STARTER, PROFESSIONAL, ENTERPRISE

### Role Hierarchy
OWNER(7) > ADMIN(6) > PM(5) > ESTIMATOR(4) > ACCOUNTANT(3) > FIELD_WORKER(2) > READ_ONLY(1)

### URL Structure
```
/api/v1/auth/          # Login, register, verify, password reset
/api/v1/users/         # User profile, org switching
/api/v1/tenants/       # Organizations, memberships, invitations
/api/v1/billing/       # Subscription, portal, invoices, plans
/api/v1/webhooks/stripe/  # Stripe webhook (no auth, no CSRF)
/api/v1/{app}/         # Feature app endpoints (projects, crm, etc.)
/api/docs/             # Swagger UI (drf-spectacular)
/admin/                # Django admin
```

## Settings
- Split config: `config/settings/{base,development,production}.py`
- Environment: `.env` file with django-environ
- **Do NOT** use Django 5.x `OPTIONS.pool` with `CONN_MAX_AGE` (incompatible)

## Demo Credentials
- **Admin**: `admin@builderstream.com` / `demo1234!` (superuser + org owner)
- **Org**: Demo Construction Co. (slug: `demo-construction`)
- **Team**: pm@, estimator@, field@, accountant@, readonly@ (all `demo1234!`)

## Completed Sections
- [x] Section 1: Full scaffold (16 apps, Docker, config, requirements)
- [x] Section 2: Multi-tenant architecture (models, middleware, context, permissions, signals)
- [x] Section 3: Auth & Registration (JWT, email verify, password reset, roles, invitations, 38 tests)
- [x] Section 4: Subscription & Billing (Stripe integration, tiered plans, module-gating, webhooks)
- [x] Section 5: Project Command Center (lifecycle state machine, health scoring, dashboard, action items, activity stream)
- [🔧] Section 6: CRM & Lead Management (7 models, lead scoring, pipeline, automation - in progress)
- [ ] Section 7+: Remaining feature apps (estimating, scheduling, financials, etc.)

## Testing
```bash
cd builderstream
python -m pytest                           # Run all tests
python -m pytest apps/accounts/tests/      # Run specific app tests
python manage.py test apps.billing         # Django test runner
```

## Section 6: CRM & Lead Management (In Progress)

### Models (7 total)
- **Contact**: CRM contacts (leads, clients, vendors) with lead scoring (0-100), referral tracking
- **Company**: Organizations for contacts with compliance tracking (insurance, licenses)
- **PipelineStage**: Configurable sales stages with auto-actions, is_won/is_lost flags (8 default stages seeded on org creation)
- **Lead**: Sales opportunities with Deal→Lead migration, estimated value, urgency, conversion tracking
- **Interaction**: Communication log (email, phone, SMS, site visit, meeting, note) with direction tracking
- **AutomationRule**: CRM workflow automation with trigger/action JSONField configs
- **EmailTemplate**: Templates with variable substitution ({{first_name}}, {{project_type}}, etc.)

### Services
- **LeadScoringService**: 0-100 score (value 30pts, urgency 20pts, source 20pts, engagement 20pts, response time 10pts)
- **LeadConversionService**: Convert lead→project, links contact as client, moves to Won stage
- **AutomationEngine**: 6 action types (SEND_EMAIL, CREATE_TASK, ASSIGN_LEAD, CHANGE_STAGE, NOTIFY_USER, SEND_SMS)

### Celery Tasks
- **process_time_based_automations**: Every 15min, check inactive leads
- **calculate_lead_scores**: Hourly, recalculate all active lead scores
- **send_follow_up_reminders**: Daily 9am, notify users of leads needing follow-up

### Known Issues
- **has_module_access permission**: Factory function implementation has issues with DRF permission instantiation (workaround: use IsOrganizationMember only, or fix factory pattern)
- Module key case sensitivity: Must use lowercase enum values ("crm", not "CRM") when calling has_module_access()

## Common Pitfalls
- `timezone` CharField on User model shadows `django.utils.timezone` — use `from django.utils import timezone as django_tz`
- Signal auto-creates OWNER membership — don't manually create in tests (unique constraint)
- Paginated ListAPIView responses: access via `data["results"]`, not `data`
- Stripe errors expected in dev with dummy API key — signals catch and log
- `.env` must use Docker service names: `DB_HOST=db`, `redis://redis:6379`
- **Module keys are lowercase**: ActiveModule enum values are lowercase strings ("crm", "project_center"), not uppercase
