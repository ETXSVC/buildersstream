# BuilderStream

Construction management SaaS platform built with Django 5.x, Django REST Framework, Celery, and PostgreSQL.

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

## Project Structure

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
│   └── analytics/   # Reporting engine, dashboards, KPIs
├── frontend/        # React SPA
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

| App | Endpoint | Description |
|-----|----------|-------------|
| Auth | `/api/v1/auth/` | Registration, login, JWT tokens, password reset |
| Users | `/api/v1/users/` | Profile, organizations |
| Tenants | `/api/v1/tenants/` | Organizations, memberships |
| Billing | `/api/v1/billing/` | Plans, subscriptions |
| Projects | `/api/v1/projects/` | Project CRUD and lifecycle |
| CRM | `/api/v1/crm/` | Contacts, pipeline, deals |
| Estimating | `/api/v1/estimating/` | Cost codes, estimates, line items |
| Scheduling | `/api/v1/scheduling/` | Crews, schedule tasks |
| Financials | `/api/v1/financials/` | Budgets, invoices, change orders |
| Clients | `/api/v1/clients/` | Portal access, selections |
| Documents | `/api/v1/documents/` | Folders, files, RFIs, submittals |
| Field Ops | `/api/v1/field-ops/` | Daily logs, time entries, expenses |
| Quality & Safety | `/api/v1/quality-safety/` | Inspections, incidents, checklists |
| Payroll | `/api/v1/payroll/` | Pay periods, records, certified payroll |
| Service | `/api/v1/service/` | Tickets, warranties |
| Analytics | `/api/v1/analytics/` | Dashboards, reports, KPIs |

Interactive API documentation is available at `/api/docs/`.

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
