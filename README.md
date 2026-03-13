# BuilderStream

Construction management SaaS platform built with Django 5.x, Django REST Framework, Celery, and PostgreSQL.

## Implementation Status

✅ **All core sections and platform sprints complete.** The platform is feature-complete.

| Module | Status | Notes |
|--------|--------|-------|
| Scaffold (Sections 1–4) | ✅ | Django 5.x, multi-tenant, JWT auth, Stripe billing |
| Project Command Center | ✅ | State machine, health scoring, Gantt, activity stream |
| CRM & Lead Management | ✅ | 7 models, lead scoring, pipeline automations |
| Estimating & Takeoffs | ✅ | 9 models, PDF/Excel export, e-signature |
| Client Portal | ✅ | Magic-link JWT, selections, approvals |
| Document & Photo Control | ✅ | S3 presigned URLs, versioning, RFIs, submittals |
| Scheduling & Resources | ✅ | CPM algorithm, Gantt, crews, equipment |
| Financial Management | ✅ | Job costing, invoicing, change orders, POs, dunning |
| Field Operations | ✅ | GPS clock-in/out, daily logs, geofencing, expenses |
| Quality & Safety | ✅ | Inspections, deficiencies, incidents, OSHA |
| Payroll | ✅ | Certified payroll, pay periods, workforce analytics |
| Service & Warranty | ✅ | Tickets, dispatch board, SLAs |
| Analytics | ✅ | KPI engine, report builder, Excel/PDF export |
| Integrations | ✅ | QuickBooks hooks, webhooks, public API keys, weather |
| Mobile / PWA | ✅ | Service worker, offline sync, geofencing |

**Platform Sprints:**
- ✅ **Sprint 1:** ASGI/Channels, 2FA TOTP, Audit logs, WebSocket notifications
- ✅ **Sprint 2:** Kanban board, white-label branding, notification bell
- ✅ **Sprint 3:** Threaded comments, universal search, command palette (⌘K)
- ✅ **Sprint 4:** Issue Tracking (SLA/escalation), Dunning Workflows, Client Payment Portal (`/pay/:token`), Custom Fields Engine

## Architecture

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: React 18 + Vite + TailwindCSS (separate SPA)
- **Database**: PostgreSQL 16
- **Cache/Broker**: Redis 7
- **Task Queue**: Celery with django-celery-beat
- **Auth**: JWT (SimpleJWT) + django-allauth, email-only (no username)
- **Storage**: AWS S3 via django-storages
- **Billing**: Stripe subscriptions
- **API Docs**: drf-spectacular (OpenAPI/Swagger)
- **Admin UI**: django-jazzmin (Bootstrap 5, dark sidebar, custom icons per model)

## Project Structure

### Repository Root

```
buildersstream/
├── builderstream/   # Django app (source of truth)
├── Documentation/   # Spec files and implementation plans
├── Logos/           # Brand assets
├── website/         # Marketing website
├── README.md        # This file
└── FEATURES.md      # Full feature specification
```

### Django App (`builderstream/`)

```
builderstream/
├── config/          # Django settings, URLs, Celery, WSGI/ASGI
├── apps/
│   ├── core/        # Shared models, mixins, permissions
│   ├── tenants/     # Multi-tenant organizations
│   ├── accounts/    # Custom User, auth, registration
│   ├── billing/     # Stripe subscriptions, plans
│   ├── projects/    # Project Command Center
│   ├── crm/         # Leads, pipeline, contacts
│   ├── estimating/  # Takeoffs, cost database, proposals
│   ├── scheduling/  # Gantt, resource allocation, crews
│   ├── financials/  # Job costing, invoicing, change orders
│   ├── clients/     # Client portal, approvals, selections
│   ├── documents/   # Doc management, RFIs, submittals
│   ├── field_ops/   # Daily logs, time tracking, expenses
│   ├── quality_safety/ # Inspections, safety, OSHA compliance
│   ├── payroll/     # Payroll processing, certified payroll
│   ├── service/     # Service tickets, warranty, maintenance
│   ├── analytics/   # Reporting engine, dashboards, KPIs
│   ├── issue_tracking/ # Issue tracker, SLA timers, escalation
│   └── custom_fields/  # Org-scoped custom field engine
├── frontend/        # React 18 + TypeScript SPA (Vite)
├── templates/       # Django templates (admin, emails)
├── requirements/    # Pip requirements (base, dev, production)
└── docker-compose.yml
```

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone and enter the project
cd builderstream

# 2. Copy environment file and update hosts for Docker
cp .env.example .env
# IMPORTANT: Change these in .env for Docker:
#   DB_HOST=db              (not localhost)
#   CELERY_BROKER_URL=redis://redis:6379/0    (not localhost)
#   CELERY_RESULT_BACKEND=redis://redis:6379/0

# 3. Start all services
docker compose up -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Seed demo data (creates superuser + org + sample team)
docker compose exec web python manage.py create_demo_org
# Login: admin@builderstream.com / demo1234!

# Or create your own superuser:
docker compose exec web python manage.py createsuperuser

# 6. Access the application
#    Home:     http://localhost:8000/         (redirects to API docs)
#    API Docs: http://localhost:8000/api/docs/
#    Admin:    http://localhost:8000/admin/
#    Frontend: http://localhost:5173/
```

### Docker Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| db | postgres:16 | 5432 | PostgreSQL database |
| redis | redis:7-alpine | 6379 | Cache and Celery broker |
| web | builderstream-web | 8000 | Django dev server |
| celery_worker | builderstream-web | - | Async task worker |
| celery_beat | builderstream-web | - | Periodic task scheduler |
| frontend | node:20 | 5173 | React SPA (Vite) |

### Local Development (Without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements/development.txt

# 3. Copy environment file and configure
cp .env.example .env

# 4. Ensure PostgreSQL and Redis are running locally

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver

# 8. Start Celery worker (separate terminal)
celery -A config worker -l info

# 9. Start Celery beat (separate terminal)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Authentication & Registration

BuilderStream uses **email-only authentication** with UUID primary keys and JWT tokens.

### User Model

Custom `AbstractBaseUser + PermissionsMixin` with:
- UUID primary key (no auto-increment)
- Email as sole login identifier (no username field)
- `email_verified` flag with token-based verification
- `last_active_organization` FK for org context switching
- Timezone preference (US timezones)
- Notification preferences (JSONField)

### Auth Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register/` | POST | Public | Create user + org + membership, returns JWT |
| `/api/v1/auth/login/` | POST | Public | Authenticate, returns JWT + user profile + orgs |
| `/api/v1/auth/token/refresh/` | POST | Public | Refresh JWT access token |
| `/api/v1/auth/verify-email/` | GET | Public | Verify email with `?token=` query param |
| `/api/v1/auth/resend-verification/` | POST | Auth | Resend verification email |
| `/api/v1/auth/forgot-password/` | POST | Public | Send password reset email |
| `/api/v1/auth/reset-password/` | POST | Public | Reset password with token |
| `/api/v1/auth/change-password/` | POST | Auth | Change password (requires old password) |
| `/api/v1/auth/invite/accept/` | POST | Public | Accept org invitation, returns JWT |
| `/api/v1/auth/oauth/google/` | POST | Public | Google OAuth (scaffolded) |
| `/api/v1/auth/oauth/github/` | POST | Public | GitHub OAuth (scaffolded) |
| `/api/v1/users/me/` | GET, PATCH | Auth | User profile |
| `/api/v1/users/me/organizations/` | GET | Auth | List user's organizations |

### Registration Flow

1. `POST /api/v1/auth/register/` with email, password, first_name, last_name, company_name
2. Creates User + Organization atomically (signal auto-creates OWNER membership + default modules)
3. Sends verification email via Celery task
4. Returns JWT tokens + user info

### Login Response

Login returns enriched JWT response with user profile and organizations:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "...",
    "last_name": "...",
    "email_verified": true,
    "timezone": "America/Chicago",
    "last_active_organization": "uuid"
  },
  "organizations": [
    {"organization_id": "uuid", "organization_name": "...", "role": "owner"}
  ]
}
```

### Role-Based Access Control

| Role | Level | Description |
|------|-------|-------------|
| `owner` | 7 | Full control, billing, org deletion |
| `admin` | 6 | Manage members, modules, settings |
| `project_manager` | 5 | Full project lifecycle access |
| `estimator` | 4 | Estimating and proposals |
| `accountant` | 3 | Financial management, invoicing |
| `field_worker` | 2 | Daily logs, time tracking, expenses |
| `read_only` | 1 | View-only access |

Permission classes:
- `IsOrganizationMember` — any active member
- `IsOrganizationAdmin` — admin or owner
- `IsOrganizationOwner` — owner only
- `role_required('project_manager')` — factory function, allows role and above
- `HasModuleAccess(module_key)` — module feature gate

### Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number

### Password Reset Flow

1. `POST /api/v1/auth/forgot-password/` with email (never reveals if email exists)
2. Token stored in Redis cache with 24-hour TTL
3. Reset link sent via Celery email task
4. `POST /api/v1/auth/reset-password/` with token + new_password

## API Endpoints

All API endpoints are mounted under `/api/v1/`:

| App | Endpoint | Description | Status |
|-----|----------|-------------|--------|
| Auth | `/api/v1/auth/` | Registration, login, JWT tokens, password reset | ✅ Complete |
| Users | `/api/v1/users/` | Profile, organizations | ✅ Complete |
| Tenants | `/api/v1/tenants/` | Organizations, memberships | ✅ Complete |
| Billing | `/api/v1/billing/` | Plans, subscriptions | ✅ Complete |
| **Projects** | `/api/v1/projects/` | **Project CRUD and lifecycle** | **✅ Complete** |
| **Dashboard** | `/api/v1/dashboard/` | **Org dashboard, action items, activity** | **✅ Complete** |
| **Action Items** | `/api/v1/action-items/` | **Tasks, deadlines, alerts** | **✅ Complete** |
| **Activity** | `/api/v1/activity/` | **Org-wide activity stream** | **✅ Complete** |
| CRM | `/api/v1/crm/` | 7 models: contacts, pipeline, leads, automations | ✅ Complete |
| Estimating | `/api/v1/estimating/` | 9 models, PDF/Excel export, e-signature | ✅ Complete |
| Scheduling | `/api/v1/scheduling/` | CPM, Gantt, crews, equipment | ✅ Complete |
| Financials | `/api/v1/financials/` | Job costing, invoicing, change orders, POs, dunning | ✅ Complete |
| Clients | `/api/v1/clients/` | Magic-link portal, selections, approvals | ✅ Complete |
| Documents | `/api/v1/documents/` | S3 presigned URLs, versioning, RFIs, submittals | ✅ Complete |
| Field Ops | `/api/v1/field-ops/` | GPS clock-in/out, daily logs, expenses | ✅ Complete |
| Quality & Safety | `/api/v1/quality-safety/` | Inspections, incidents, OSHA | ✅ Complete |
| Payroll | `/api/v1/payroll/` | Certified payroll, workforce analytics | ✅ Complete |
| Service | `/api/v1/service/` | Tickets, dispatch board, warranties | ✅ Complete |
| Analytics | `/api/v1/analytics/` | KPI engine, report builder, exports | ✅ Complete |
| Issue Tracking | `/api/v1/issue-tracking/` | SLA timers, escalation rules, canned responses | ✅ Complete |
| Custom Fields | `/api/v1/custom-fields/` | Org-scoped field definitions for any module | ✅ Complete |
| Public Invoice | `/api/v1/financials/public/invoices/{token}/` | Unauthenticated invoice view + Stripe payment | ✅ Complete |

Interactive API documentation is available at `/api/docs/`.

### Project Management Endpoints (Section 5)

**Project CRUD:**
- `GET /api/v1/projects/` — List projects with filtering (status, type, health, archived)
- `POST /api/v1/projects/` — Create project (auto-generates project number `BSP-{YEAR}-{SEQ}`)
- `GET /api/v1/projects/{pk}/` — Project detail with team members and milestones
- `PUT/PATCH /api/v1/projects/{pk}/` — Update project
- `DELETE /api/v1/projects/{pk}/` — Delete project

**Project Lifecycle:**
- `POST /api/v1/projects/{pk}/transition-status/` — Transition status with stage-gate validation
- `GET /api/v1/projects/{pk}/transitions/` — View transition audit trail

**Project Team & Milestones:**
- `GET/POST/DELETE /api/v1/projects/{pk}/team-members/` — Manage team members with roles
- `GET/POST /api/v1/projects/{pk}/milestones/` — Manage project milestones

**Project Activity:**
- `GET /api/v1/projects/{pk}/activity/` — View project activity log (last 50 entries)

**Dashboard:**
- `GET /api/v1/dashboard/` — Organization dashboard (cached 60s)
  - Active projects count and status distribution
  - Financial snapshot (estimated/actual values and costs)
  - Schedule overview (on-track/at-risk/behind counts)
  - Action items (top 20 unresolved)
  - Activity stream (last 50 entries)
- `GET/PUT /api/v1/dashboard/layout/` — User's dashboard widget layout

**Action Items:**
- `GET /api/v1/action-items/` — List action items with filtering
- `POST /api/v1/action-items/` — Create action item
- `GET /api/v1/action-items/{pk}/` — Action item detail
- `PUT/PATCH /api/v1/action-items/{pk}/` — Update (auto-sets `resolved_at`)
- `DELETE /api/v1/action-items/{pk}/` — Delete action item

**Activity Stream:**
- `GET /api/v1/activity/` — Organization-wide activity stream (paginated)

## Multi-Tenancy

BuilderStream uses **row-level organization-based multi-tenancy** with thread-local isolation:

### Architecture

- **`TenantModel`** abstract base: auto-links records to an organization via FK; auto-filters querysets using `TenantManager`
- **`TenantManager`**: custom manager that reads thread-local storage to auto-scope all queries to the current organization
  - `.for_organization(org)` — explicit filter bypassing thread-local
  - `.unscoped()` — admin/system access without filtering
- **`TenantMiddleware`** (`apps.tenants.middleware`): resolves organization context per-request via:
  1. `X-Organization-ID` header (API clients)
  2. `user.last_active_organization` field (default)
  3. First active membership (fallback)
- **Thread-local context** (`apps.tenants.context`): `set_current_organization()`, `get_current_organization()`, `tenant_context()` context manager for Celery tasks

### Organization Model

| Field | Description |
|-------|-------------|
| `name`, `slug` | Identity with unique slug for URL routing |
| `owner` | FK to User (PROTECT) |
| `industry_type` | Residential Remodel, Custom Home, Commercial GC, Specialty Trade, Roofing, Enterprise |
| `subscription_plan` | Starter, Professional, Enterprise, Trial |
| `subscription_status` | Active, Past Due, Canceled, Trialing |
| `stripe_customer_id` | Stripe integration (auto-created via signal) |
| `max_users` | Seat limit per subscription |
| `settings` | JSONField for org-level config (timezone, fiscal year, currency) |

### Module System

Organizations can activate/deactivate feature modules. Always-active modules: **Project Center**, **Analytics**.

Available modules: Project Center, CRM, Estimating, Scheduling, Financials, Client Portal, Documents, Field Ops, Quality & Safety, Payroll, Service & Warranty, Analytics.

Use `HasModuleAccess('module_key')` permission class to gate views by active module.

### Tenant API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tenants/organizations/` | GET, POST | List/create organizations |
| `/api/v1/tenants/organizations/{slug}/` | GET, PUT, DELETE | Organization detail |
| `/api/v1/tenants/memberships/` | GET, POST | List/manage members |
| `/api/v1/tenants/memberships/invite/` | POST | Invite member by email |
| `/api/v1/tenants/modules/` | GET, POST, PUT | List/manage active modules |
| `/api/v1/tenants/switch-organization/` | POST | Switch active organization |

### Management Commands

```bash
# Create demo organization with sample users and all modules
python manage.py create_demo_org

# Options:
#   --owner-email   Owner email (default: admin@builderstream.com)
#   --org-name      Organization name (default: Demo Construction Co.)
#   --no-sample-users  Skip sample team members
```

## Testing

```bash
# Run all tests
docker compose exec web pytest

# Run auth tests only
docker compose exec web pytest apps/accounts/tests/test_auth.py -v

# Run with coverage
docker compose exec web pytest --cov=apps --cov-report=term-missing
```

## Environment Variables

See `.env.example` for all required configuration variables.

## Demo Credentials

| User | Email | Password |
|------|-------|----------|
| Admin (superuser + org owner) | admin@builderstream.com | demo1234! |
| Project Manager | pm@builderstream.com | demo1234! |
| Estimator | estimator@builderstream.com | demo1234! |
| Field Worker | field@builderstream.com | demo1234! |
| Accountant | accountant@builderstream.com | demo1234! |
| Read Only | readonly@builderstream.com | demo1234! |

**Org:** Demo Construction Co. (slug: `demo-construction`)

## Development on a Remote VPS

You can run the full stack on a remote Ubuntu VPS (e.g. Contabo) and connect to it from your local machine via VS Code Remote-SSH.

### Setup

```bash
# 1. Install Docker on the VPS
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER && newgrp docker

# 2. Clone and configure
git clone https://github.com/ETXSVC/buildersstream.git /opt/builderstream
cd /opt/builderstream/builderstream
cp .env.example .env   # then fill in your values

# 3. Open firewall ports
ufw allow OpenSSH && ufw allow 5173 && ufw allow 8000 && ufw enable

# 4. Start
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_demo_org
```

### Access

```
http://<vps-ip>:5173/           # React frontend (Vite dev server — HTTP only, not HTTPS)
http://<vps-ip>:8000/api/docs/  # Django API docs
http://<vps-ip>:8000/admin/     # Django admin
```

> **Important:** Vite's dev server does not use TLS. Always use `http://` — using `https://` will show a browser security error.

### Remote Access Config

Three settings must be correct for the app to work from a remote IP:

1. **`ALLOWED_HOSTS`** — `config/settings/development.py` sets `ALLOWED_HOSTS = ["*"]`. The Vite proxy rewrites the `Host` header to `web:8000`; if `web` is not allowed, Django returns 400 for every proxied request.

2. **`VITE_API_URL`** — must be **unset** in `docker-compose.yml`. The frontend uses relative paths (`/api/...`) proxied by Vite to `http://web:8000`. Setting it to `http://localhost:8000` causes the browser to call Django directly, failing from any remote machine.

3. **Vite HMR** — `vite.config.ts` must not set `hmr.host: 'localhost'`. Without it, Vite auto-uses the page hostname for the HMR WebSocket, working from any IP.

Add to `.env` on the VPS so email links resolve correctly:
```bash
FRONTEND_URL=http://<vps-ip>:5173
```

### VS Code Remote-SSH

1. Install the **Remote - SSH** extension
2. `Ctrl+Shift+P` → **Remote-SSH: Connect to Host** → `root@<vps-ip>`
3. Open `/opt/builderstream` — edit files directly on the VPS with full IntelliSense
4. Use the integrated terminal to run `docker compose logs -f`

### Production Deployment (Recommended)

For production or a more managed dev environment, use **Coolify** (free, self-hosted PaaS):

```bash
# Installs on Ubuntu in ~2 minutes
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
# Then open http://<vps-ip>:8000 to configure
```

Coolify detects `docker-compose.yml` automatically and handles SSL certificates, nginx, and auto-deploy on `git push`.

## Known Issues & Fixes

### Service Worker — API Requests Must Bypass SW
The PWA service worker must **not** intercept `/api/` requests (GET or mutations). Intercepting auth endpoints prevents `Set-Cookie` response headers from being processed by the browser natively, causing the login POST to hang and creating stale-auth redirect loops in Chrome and Edge. All `/api/` traffic bypasses the SW entirely; React Query handles client-side caching.

**Cache version:** `builderstream-v4` — bump this whenever the SW fetch strategy changes to force re-installation.

If login hangs or causes a redirect loop after a service worker update:
1. DevTools → Application → Service Workers → **Unregister**
2. DevTools → Application → Cache Storage → delete all `builderstream-*` entries
3. Hard reload (`Ctrl+Shift+R`)

### Project Edit Form — Blank Text Fields
Django model fields with `blank=True` but not `null=True` reject `null` values from DRF. The project PATCH payload sends `''` (empty string) for text fields (`description`, `address`, `city`, `state`) and `null` only for genuinely nullable fields (`estimated_value`, `start_date`, `estimated_completion`, `actual_completion`).

### Signal Memory Leak Pattern

Django signals that detect status changes must **never** use module-level dicts as a status cache. The pattern `_status_cache = {}` accumulates entries forever if a save raises an exception after `pre_save` fires but before `post_save` runs (the `pop()` never executes). Always store the old value on the instance instead:

```python
# WRONG — module-level dict leaks on save failure
_cache = {}

@receiver(pre_save, sender=MyModel)
def cache_status(sender, instance, **kwargs):
    if instance.pk:
        _cache[instance.pk] = instance.status

@receiver(post_save, sender=MyModel)
def on_saved(sender, instance, created, **kwargs):
    old = _cache.pop(instance.pk, None)  # never runs if save raised

# CORRECT — instance attribute, GC'd with the object
@receiver(pre_save, sender=MyModel)
def cache_status(sender, instance, **kwargs):
    if instance.pk:
        instance._old_status = instance.status

@receiver(post_save, sender=MyModel)
def on_saved(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_status", None)
```

This fix has been applied to `apps/service/signals.py`, `apps/payroll/signals.py`, and `apps/field_ops/signals.py`.

### White-Label Branding
`useApplyBranding()` (called once in `ResponsiveLayout`) applies CSS custom properties to `:root` and injects a `<style>` tag for custom CSS. All three layout components (`DesktopLayout`, `TabletLayout`, `MobileLayout`) call `useBranding()` to render `company_name` and `logo_url` in the header. Saving on the Branding settings page invalidates the React Query `['branding']` cache — the header updates live without a page reload.

CSS variable defaults are defined in `frontend/src/index.css` under `:root`. Semantic classes (`.bs-sidebar`, `.bs-sidebar-link-active`, `.bs-primary-icon`) reference these variables so branding changes propagate without inline styles.
