# BuilderStream

A full-featured SaaS platform for construction management companies. Covers the entire project lifecycle from lead capture through project closeout, payroll, field operations, and client billing.

## Live Site

**https://buildersstream.online** (note double-s)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework, Channels (WebSocket) |
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Recharts |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis (3 DBs: broker, cache, channels) |
| Task Queue | Celery + Celery Beat |
| Auth | SimpleJWT, 2FA TOTP |
| File Storage | Local filesystem (Apache-served via `/media/`) |
| Deployment | Docker Compose + Apache2 reverse proxy + Let's Encrypt SSL |

## Architecture Overview

```
Apache2 (SSL termination)
   ├── /api/        → Gunicorn (Django ASGI via uvicorn)
   ├── /admin/      → Gunicorn
   ├── /ws/         → Django Channels (WebSocket)
   ├── /static/     → Whitenoise via Gunicorn
   ├── /media/      → Apache Alias → /var/www/.../media/
   └── /            → Apache Alias → frontend/dist/ (React SPA)
```

Multi-tenancy is row-level via `organization` FK on every model. The `TenantMiddleware` resolves org context from the `X-Organization-ID` request header.

## Modules (18 Django Apps)

| App | Description |
|-----|-------------|
| `core` | Shared utilities, base models |
| `tenants` | Organizations, memberships, RBAC roles |
| `accounts` | Users, 2FA TOTP, JWT auth |
| `billing` | Stripe subscriptions, invoices, usage metering, dunning, client payment portal |
| `projects` | Project lifecycle state machine, milestones, health scoring, Kanban |
| `crm` | Contacts, leads, pipeline stages, automation rules, lead scoring |
| `estimating` | Estimates, line items, proposals |
| `scheduling` | Tasks, Gantt chart, crews, equipment |
| `financials` | Invoices, budgets, expenses, change orders, purchase orders, cash flow |
| `clients` | Client records |
| `documents` | Documents, folders, RFIs, submittals, photos |
| `field_ops` | Time tracking (clock in/out), daily logs, field expenses |
| `quality_safety` | Inspections, deficiencies, safety incidents |
| `payroll` | Pay runs, certified payroll, employees/contractors, workforce summary |
| `service` | Service requests, warranties, warranty claims |
| `analytics` | KPI reports, saved reports |
| `issue_tracking` | Issues, SLA timers, escalation rules, issue types |
| `custom_fields` | Custom field definitions and values (GenericFK) |

## Frontend Structure

```
frontend/src/
├── features/
│   ├── dashboard/          # Home dashboard (5 widgets)
│   ├── projects/           # Projects list, detail, Kanban, comments
│   ├── crm/                # Leads, contacts, pipeline
│   ├── financials/         # Invoices, expenses, change orders, POs, budgets
│   ├── scheduling/         # Tasks, Gantt view, crews, equipment
│   ├── field-ops/          # Time entries, daily logs, expenses, camera, clock
│   ├── documents/          # Documents, RFIs, submittals, photos
│   ├── estimating/         # Estimates, proposals
│   ├── quality-safety/     # Inspections, deficiencies, safety incidents
│   ├── service/            # Service requests, warranties, claims
│   ├── payroll/            # Pay runs, employees, certified payroll
│   ├── analytics/          # KPI reports
│   ├── issues/             # Issue tracking with SLA
│   ├── collaboration/      # Team channels + DMs (WebSocket)
│   ├── settings/           # Org settings, branding, custom fields, dunning
│   └── auth/               # Login, register, 2FA, password reset
├── components/
│   └── KpiCard.tsx         # Shared dashboard KPI card
├── hooks/                  # React Query hooks per module
├── api/                    # API client functions per module
└── types/                  # TypeScript interfaces per module
```

Each section page has a **dashboard section at the top** with KPI cards and Recharts charts (bar/pie) derived live from API data.

## Running Locally (Docker)

```bash
git clone <repo>
cd builderstream

# Configure environment
cp .env.example .env   # fill in DB_PASSWORD, etc.

# Start all services
docker compose up -d

# Apply migrations
docker compose exec web python manage.py migrate

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Create demo org + admin user
docker compose exec web python manage.py create_demo_org

# Start frontend dev server
cd frontend && npm install && npm run dev
```

Access:
- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/  (admin@builderstream.com / demo1234!)

## Production Deployment

The site runs on a VPS with:
- Docker Compose (`docker-compose.prod.yml`) for Django + Celery + Redis + PostgreSQL
- Apache2 as the reverse proxy and static file server
- Certbot (Let's Encrypt) for SSL at `/etc/letsencrypt/live/buildersstream.online-0001/`
- Apache config at `/etc/apache2/sites-available/builderstream.online.conf`

```bash
# Deploy new code
git pull
cd frontend && npm run build
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
sudo systemctl reload apache2
```

## Key Patterns

- **Multi-tenancy**: `TenantModel` → `TenantManager` → `TenantMiddleware` → `TenantViewSetMixin`
- **Auth**: Email-only login, SimpleJWT, `X-Organization-ID` header required on all API calls
- **Services**: Business logic lives in `apps/<app>/services.py`, not views
- **Signals**: Side effects (activity logs, defaults) in `apps/<app>/signals.py`
- **Celery**: All tasks use `tenant_context(org)` and `.iterator()` on querysets
- **Dashboards**: Each module page prefixes its table/list with KPI cards + Recharts charts

## Client Payment Portal

Public (no auth) invoice payment page at `/pay/:token` — clients receive a tokenized link by email to pay invoices via Stripe.

## API Authentication

```http
Authorization: Bearer <access_token>
X-Organization-ID: <uuid>
```

Get tokens via `POST /api/v1/accounts/token/` with `{ email, password }`.

## Environment Variables

See `.env` for all required variables. Key ones:

```env
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=buildersstream.online,www.buildersstream.online
DB_HOST=db
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
REDIS_CHANNELS_URL=redis://redis:6379/2
STRIPE_SECRET_KEY=sk_...
```

## Known Issues / Gotchas

See `CLAUDE.md` for a full list of pitfalls. Key ones:
- `MEDIA_URL` must have a leading slash (`/media/`)
- `Content-Type` must be `undefined` (not set manually) for multipart uploads from axios
- `REDIS_CHANNELS_URL` must be set separately from the broker URL
- `has_module_access()` permission factory has DRF instantiation issues — use `IsOrganizationMember` as workaround in CRM views
