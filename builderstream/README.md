# BuilderStream v3.3.0

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

## Modules (19 Django Apps)

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
| `teams` | Teams (crew groups), members linked to payroll employees, project assignment |

## Teams Feature

Org admins can create named **Teams** (e.g. "Framing Crew") and assign them to projects. Team members are linked to `payroll.Employee` records — W-2 and 1099 contractors both supported; no platform login required.

- **Company → Teams tab**: create/delete teams, expand to add/remove members, assign Lead/Member roles
- **Company → Team Members tab**: combined workforce view (all W-2 + contractors)
- **Projects**: Assigned Team field in create/edit modal; team name shown on project cards
- **API**: `GET/POST /api/v1/teams/`, `POST /api/v1/teams/{id}/add-member/`, `DELETE /api/v1/teams/{id}/remove-member/{employee_id}/`

## Collaboration — Channel Archive & Restore

Hover any channel or DM in the Team Messaging sidebar to reveal a `•••` menu:
- **Archive** (channels) / **Close** (DMs) — removes from active list immediately
- **Archived** section at sidebar bottom (collapsed by default) — expand to see all archived; hover → **Restore**

**API**: `POST /api/v1/collaboration/channels/{id}/archive/`, `POST /api/v1/collaboration/channels/{id}/unarchive/`, `GET /api/v1/collaboration/channels/?is_archived=true`

## Session Security

- **30-minute idle logout**: `hydrate()` uses `rawClient` (no interceptors) — returning to the app after 30+ min idle triggers 401 → redirect to `/login`. No silent refresh on page load.
- **Active session**: `apiClient` interceptor silently refreshes the access token on 401 during active use; failed refresh → redirect to `/login`.

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
│   ├── collaboration/      # Team channels + DMs (WebSocket) + archive/restore
│   ├── company/            # Employees, contractors, Team Members, Teams
│   ├── settings/           # Org settings, branding, custom fields, dunning
│   └── auth/               # Login, register, 2FA, password reset
├── components/
│   └── KpiCard.tsx         # Shared clickable KPI card
├── hooks/                  # React Query hooks per module
├── api/                    # API client functions per module
└── types/                  # TypeScript interfaces per module
```

Each section page has a **dashboard section at the top** with KPI cards and Recharts charts. All KPI cards are **clickable** — clicking navigates to the relevant tab or applies the relevant filter.

## E2E Tests (Playwright)

```bash
cd frontend
npm run test:e2e          # run all 74 tests (headless, 2 workers)
npm run test:e2e:headed   # watch mode
npm run test:e2e:report   # open last HTML report
```

Tests run against `https://buildersstream.online` by default. Override with `BASE_URL=http://localhost:4173 npm run test:e2e`.

| Spec file | Tests | Coverage |
|-----------|-------|----------|
| `auth.spec.ts` | 4 | Login, wrong password, logout |
| `dashboard.spec.ts` | 4 | Widgets, refresh, analytics link |
| `crm.spec.ts` | 6 | KPI nav, create contact, search, subnav |
| `projects.spec.ts` | 17 | KPI nav, create/edit/delete, filter, search, Kanban, detail link |
| `navigation.spec.ts` | 26 | All 8 sidebar links, header, command palette, direct URLs, sign out |
| `collaboration.spec.ts` | 6 | Channels, create channel, DM modal, subnav |
| `financials.spec.ts` | 6 | KPI nav, tab switching, invoice modal, subnav |
| `field-ops.spec.ts` | 6 | KPI nav, tab switching, clock-in button |
| `company.spec.ts` | 7 | KPI cards, tabs, Team Members tab, Add Employee modal |
| `teams.spec.ts` | 7 | Teams KPI, tab, create team, expand members, project selector |

Auth state is cached in `frontend/e2e/.auth/user.json` by `global-setup.ts` and reused across all tests.

## Running Locally (Docker)

```bash
git clone <repo>
cd builderstream

cp .env.example .env   # fill in DB_PASSWORD, SECRET_KEY, etc.

docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py create_demo_org

cd frontend && npm install && npm run dev
```

Access:
- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/  (admin@builderstream.com / demo1234!)

## Production Deployment

```bash
git pull
cd frontend && npm run build
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
sudo systemctl reload apache2
```

- Apache config: `/etc/apache2/sites-available/builderstream.online.conf`
- SSL certs: `/etc/letsencrypt/live/buildersstream.online-0001/`

## Key Patterns

- **Multi-tenancy**: `TenantModel` → `TenantManager` → `TenantMiddleware` → `TenantViewSetMixin`
- **Auth**: Email-only login, SimpleJWT, `X-Organization-ID` header required on all API calls
- **Services**: Business logic in `apps/<app>/services.py`, not views
- **Signals**: Side effects in `apps/<app>/signals.py`
- **Celery**: All tasks use `tenant_context(org)` and `.iterator()` on querysets
- **Dashboards**: Each module page prefixes tables with KPI cards + Recharts charts

## API Authentication

```http
Authorization: Bearer <access_token>
X-Organization-ID: <uuid>
```

Get tokens via `POST /api/v1/accounts/token/` with `{ email, password }`.

## Known Issues / Gotchas

See `CLAUDE.md` for the full list of pitfalls. Key ones:
- `MEDIA_URL` must have a leading slash (`/media/`)
- `Content-Type` must be `undefined` for multipart uploads from axios
- `REDIS_CHANNELS_URL` must be set separately from the broker URL
- `has_module_access()` permission factory has DRF instantiation issues — use `IsOrganizationMember` as workaround in CRM views
- `apps.teams` must appear in `LOCAL_APPS` and `config/urls.py`; restart web container after adding

## Changelog

### v3.3.0 (2026-03-17)
- **Teams**: New `apps.teams` (19th app) — `Team` + `TeamMember` models, full CRUD API (`/api/v1/teams/`), UI under Company page
- **Company page**: Team Members tab shows all employees + contractors combined; new Teams KPI card and tab
- **Projects**: Assigned Team field in modal; team name on project cards
- **Collaboration**: Archive/restore channels and DMs via `•••` sidebar menu; `unarchive` endpoint; `?is_archived=true` query param
- **Session security**: 30-min idle logout; `hydrate()` no longer silently refreshes tokens
- **E2E**: 44 → 74 tests (projects: 6→17, navigation: 5→26; new company + teams specs)
- **Security**: `MembershipViewSet` role hierarchy enforcement on invite and role update

### v3.2.0
- Sidebar "Team" renamed to "Team Messaging"
- Full platform feature-complete: 18 Django apps, 11 module pages

### v3.1.0
- Initial feature-complete release: all sections, sprints, and E2E baseline
