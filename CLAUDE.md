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
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS (in `builderstream/frontend/`)
- **Database**: PostgreSQL 16 with UUID primary keys
- **Auth**: JWT via SimpleJWT, email-only (no username)
- **Multi-tenancy**: Row-level isolation via thread-local storage (not schema-based)
- **Billing**: Stripe subscriptions with per-seat pricing

### App Structure (16 apps)
```
builderstream/apps/
  core/           # Base models (TimeStampedModel, TenantModel), permissions
  tenants/        # Organization, Membership, ActiveModule, middleware, context
  accounts/       # User model, JWT auth, registration, invitations
  billing/        # Stripe billing, plans, webhooks, subscription enforcement
  projects/       # Project Command Center: lifecycle, health, dashboard, action items, activity
  crm/            # CRM & Lead Management: 7 models, pipeline, scoring, automation, analytics
  estimating/     # Estimating & takeoffs: 9 models, proposals, e-signature, PDF/Excel export
  clients/        # Client portal: selections, approvals, messaging, magic-link JWT auth
  documents/      # Document & photo control: RFIs, submittals, versioning, S3 presigned URLs
  scheduling/     # Scheduling & resource management: Gantt, CPM, crews, equipment
  financials/     # Financial management suite (Section 11 — next)
  field_ops/      # Field operations hub (Section 12)
  quality_safety/ # Quality & safety compliance (Section 13)
  payroll/        # Payroll & workforce management (Section 14)
  service/        # Service & warranty management (Section 15)
  analytics/      # Analytics & reporting engine (Section 16)
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
/api/v1/auth/             # Login, register, verify, password reset
/api/v1/users/            # User profile, org switching
/api/v1/tenants/          # Organizations, memberships, invitations
/api/v1/billing/          # Subscription, portal, invoices, plans
/api/v1/webhooks/stripe/  # Stripe webhook (no auth, no CSRF)
/api/v1/projects/         # Project lifecycle, milestones, team, activity
/api/v1/dashboard/        # Cached org dashboard + layout
/api/v1/crm/              # Contacts, leads, pipeline, analytics
/api/v1/estimating/       # Estimates, takeoffs, proposals, e-signature
/api/v1/clients/          # Client portal contractor-facing endpoints
/api/v1/portal/           # Client portal client-facing endpoints (magic-link JWT)
/api/v1/documents/        # Folders, documents, RFIs, submittals, photos
/api/v1/scheduling/       # Schedules, tasks, crews, equipment, resources
/api/docs/                # Swagger UI (drf-spectacular)
/admin/                   # Django admin
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
- [x] Section 6: CRM & Lead Management (7 models, lead scoring, pipeline automation, backend complete)
- [x] Section 7: Estimating & Takeoffs (9 models, 4 services, 23 serializers, 10 viewsets, PDF/Excel export, e-signature)
- [x] Section 8: Client Collaboration Portal (7 models, 4 services, magic-link JWT, portal views, /api/v1/portal/ routes)
- [x] Section 9: Document & Photo Control (7 models, S3 presigned URLs, versioning, RFIs, submittals, photo galleries)
- [x] Section 10: Scheduling & Resource Management (4 models, 3 services, CPM algorithm, Gantt data, crew availability, equipment depreciation)
- [x] Dashboard UI: Frontend implementation (React + TypeScript, 5 widgets, customization)

## Next: Section 11 — Financial Management Suite
- Job costing with real-time variance tracking
- Budget line items, change orders, draw schedules
- AIA G702/G703 invoice format support
- QuickBooks / Xero integration hooks
- `/api/v1/financials/` endpoints

## Testing
```bash
cd builderstream
python -m pytest                           # Run all tests
python -m pytest apps/accounts/tests/      # Run specific app tests
python -m pytest -v --tb=short            # Verbose with short tracebacks
```

## Common Pitfalls
- `timezone` CharField on User model shadows `django.utils.timezone` — use `from django.utils import timezone as django_tz`
- Signal auto-creates OWNER membership — don't manually create in tests (unique constraint)
- Paginated ListAPIView responses: access via `data["results"]`, not `data`
- Stripe errors expected in dev with dummy API key — signals catch and log
- `.env` must use Docker service names: `DB_HOST=db`, `redis://redis:6379`
- **Module keys are lowercase**: ActiveModule enum values are lowercase strings ("crm", "project_center"), not uppercase
- **has_module_access permission**: Factory function has DRF instantiation issues — use `IsOrganizationMember` as workaround
- **SelectionOption** (Section 8): NOT a TenantModel — org accessible via Selection FK chain
- **DocumentAcknowledgment** (Section 9): NOT a TenantModel — org accessible via Document FK
- PostgreSQL index names max 30 chars — shorten long index names in migrations
- **TenantMiddleware + JWT**: Django middleware sees `AnonymousUser` for JWT API requests (DRF auth runs inside views, not middleware). `TenantMiddleware` has a `_try_jwt_auth()` method that manually calls `JWTAuthentication().authenticate(request)` when session user is anonymous — this is required for org context to work with Bearer tokens
- **CORS custom headers**: `X-Organization-ID` must be listed explicitly in `CORS_ALLOW_HEADERS` in `config/settings/base.py` — the default django-cors-headers allowlist does not include it
- **Redis cache URL**: `.env` needs `REDIS_CACHE_URL=redis://redis:6379/1` separately from `CELERY_BROKER_URL` — if missing, cache falls back to `localhost:6379` which fails inside Docker
- **Dashboard API shape**: `DashboardService._build_dashboard_data()` returns `project_metrics`, `financial_summary` (not `active_projects`, `financial_snapshot`) — field names must match frontend TypeScript types in `frontend/src/types/dashboard.ts`
- **Docker build context**: Requires `.dockerignore` to exclude `frontend/node_modules/` — without it the build context sends the entire node_modules tree and fails
