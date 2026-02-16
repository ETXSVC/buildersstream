# BuilderStream

Construction management SaaS platform built with Django 5.x, Django REST Framework, Celery, and PostgreSQL.

## Architecture

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: React 18 + Vite + TailwindCSS (separate SPA)
- **Database**: PostgreSQL 16 with connection pooling
- **Cache/Broker**: Redis 7
- **Task Queue**: Celery with django-celery-beat
- **Auth**: JWT (SimpleJWT) + django-allauth
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

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker compose up -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create superuser
docker compose exec web python manage.py createsuperuser

# 6. Access the application
#    API:      http://localhost:8000/api/v1/
#    Admin:    http://localhost:8000/admin/
#    API Docs: http://localhost:8000/api/docs/
#    Frontend: http://localhost:5173/
```

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

## API Endpoints

All API endpoints are mounted under `/api/v1/`:

| App | Endpoint | Description |
|-----|----------|-------------|
| Accounts | `/api/v1/accounts/` | Users, registration, JWT tokens |
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
  2. `user.active_organization` field (default)
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

### Membership Roles

| Role | Description |
|------|-------------|
| `owner` | Full control, billing, org deletion |
| `admin` | Manage members, modules, settings |
| `project_manager` | Full project lifecycle access |
| `estimator` | Estimating and proposals |
| `field_worker` | Daily logs, time tracking, expenses |
| `accountant` | Financial management, invoicing |
| `read_only` | View-only access |

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

### Permission Classes

- `IsOrganizationMember` — any active member
- `IsOrganizationAdmin` — admin or owner role
- `IsOrganizationOwner` — owner role only
- `HasModuleAccess(module_key)` — module feature gate

### Management Commands

```bash
# Create demo organization with sample users and all modules
python manage.py create_demo_org

# Options:
#   --owner-email   Owner email (default: admin@builderstream.com)
#   --org-name      Organization name (default: Demo Construction Co.)
#   --no-sample-users  Skip sample team members
```

## Environment Variables

See `.env.example` for all required configuration variables.
