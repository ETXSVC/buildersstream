# BuilderStream Pro v3.0

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/ETXSVC/buildersstream)
[![License](https://img.shields.io/badge/license-Confidential-red.svg)]()
[![Framework](https://img.shields.io/badge/framework-Django%205.2-green.svg)](https://www.djangoproject.com/)
[![Stack](https://img.shields.io/badge/stack-Django%20%7C%20React%2018%20%7C%20PostgreSQL-blue.svg)]()

> **Construction & Renovation Management Platform** — A comprehensive, modular, multi-tenant SaaS platform purpose-built for construction and renovation contractors.

## Overview

BuilderStream Pro is an all-in-one platform that unifies every aspect of the contractor workflow — from initial lead capture and estimating through project execution, financial management, and client delivery — eliminating the need for multiple disconnected software tools.

Built on **Django 5.2 + Django REST Framework**, with **React 18** frontend, **PostgreSQL 16**, **Redis 7**, and **Celery** for async operations.

### Key Features

- **16 Integrated Modules** — Project management, CRM, estimating, scheduling, financials, client portal, documents, field ops, and more
- **Multi-Tenant Architecture** — Row-level organization isolation via thread-local context (no schema-per-tenant complexity)
- **Stripe Billing** — Per-seat subscriptions with module gating (Starter / Professional / Enterprise)
- **Client Portal** — Magic-link authenticated client-facing portal for selections, approvals, and messaging
- **Real-Time Dashboard** — Redis-cached dashboard with 5 widgets, 60-second TTL, React Query frontend

---

## Technology Stack

### Backend
- **Django 5.2.x** — Web framework
- **Django REST Framework** — API layer with DRF-Spectacular (OpenAPI/Swagger)
- **SimpleJWT** — JWT authentication (email-only, no username)
- **Celery + Redis** — Async task queue and beat scheduler
- **PostgreSQL 16** — Primary database with UUID primary keys
- **django-environ** — Split settings (base / development / production)
- **Stripe** — Subscription billing with webhook processing
- **boto3 / AWS S3** — File storage with presigned URL pattern

### Frontend
- **React 18** — UI framework
- **TypeScript** — Type-safe development
- **Vite** — Build tool
- **TailwindCSS** — Utility-first styling
- **React Query (TanStack)** — Server state management
- **Zustand** — Client state management
- **Axios** — HTTP client with JWT interceptor

### Infrastructure
- **Docker Compose** — Local development (postgres, redis, web, celery-worker, celery-beat)
- **AWS S3** — Document and photo storage
- **SendGrid / SMTP** — Transactional email

---

## Architecture

### Multi-Tenancy

Row-level isolation via thread-local storage:

```
Request → TenantMiddleware → set_current_organization() → thread-local
                                        ↓
                              TenantModel.objects.all()
                              (auto-filtered via TenantManager)
```

- `TenantModel` — abstract base with `organization` FK and `TenantManager`
- `TenantMiddleware` — resolves org from `X-Organization-ID` header → `last_active_organization` → first membership
- `SubscriptionRequiredMiddleware` — enforces subscription status (active/trialing=full, past_due=read-only, canceled=402)

### App Structure (16 apps)

```
builderstream/apps/
  core/           # Base models (TimeStampedModel, TenantModel), permissions, RBAC
  tenants/        # Organization, Membership, ActiveModule, middleware, context
  accounts/       # User model, JWT auth, registration, password reset, invitations
  billing/        # Stripe subscriptions, plans, webhooks, module enforcement
  projects/       # Project lifecycle, health scoring, dashboard API, milestones, activity
  crm/            # CRM & Lead Management — contacts, pipeline, scoring, automation
  estimating/     # Estimating & takeoffs — cost items, assemblies, proposals, e-signature
  clients/        # Client portal — selections, approvals, messaging, magic-link auth
  documents/      # Document & photo control — RFIs, submittals, versioning, S3 uploads
  scheduling/     # Scheduling & resource management — Gantt, CPM, crew, equipment
  financials/     # Financial management suite (Section 11 — next)
  field_ops/      # Field operations hub (Section 12)
  quality_safety/ # Quality & safety compliance (Section 13)
  payroll/        # Payroll & workforce management (Section 14)
  service/        # Service & warranty management (Section 15)
  analytics/      # Analytics & reporting engine (Section 16)
```

### Role Hierarchy

```
OWNER(7) > ADMIN(6) > PM(5) > ESTIMATOR(4) > ACCOUNTANT(3) > FIELD_WORKER(2) > READ_ONLY(1)
```

### URL Structure

```
/api/v1/auth/             # Login, register, email verify, password reset
/api/v1/users/            # User profile, org switching
/api/v1/tenants/          # Organizations, memberships, invitations
/api/v1/billing/          # Subscription, billing portal, invoices, plans
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

---

## Build Progress

### Phase 1 — Foundation (Complete)

| # | Section | Status |
|---|---------|--------|
| 1 | Project Scaffolding & Core Config | ✅ Complete |
| 2 | Multi-Tenant Architecture | ✅ Complete |
| 3 | Authentication & User Roles | ✅ Complete |
| 4 | Subscription & Billing (Stripe) | ✅ Complete |
| 5 | Project Command Center | ✅ Complete |

### Phase 2 — Core Features (Complete)

| # | Section | Status |
|---|---------|--------|
| 6 | CRM & Lead Management | ✅ Complete |
| 7 | Estimating & Digital Takeoff Engine | ✅ Complete |
| 8 | Client Collaboration Portal | ✅ Complete |
| 9 | Document & Photo Control | ✅ Complete |

### Phase 3 — Operations (In Progress)

| # | Section | Status |
|---|---------|--------|
| 10 | Scheduling & Resource Management | ✅ Complete |
| 11 | Financial Management Suite | 🔲 Next |
| 12 | Field Operations Hub | 🔲 Pending |
| 13 | Quality & Safety Compliance | 🔲 Pending |

### Phase 4 — Enterprise (Planned)

| # | Section | Status |
|---|---------|--------|
| 14 | Payroll & Workforce Management | 🔲 Planned |
| 15 | Service & Warranty Management | 🔲 Planned |
| 16 | Analytics & Reporting Engine | 🔲 Planned |
| 17 | Integration Ecosystem & Open API | 🔲 Planned |
| 18 | Mobile / PWA Experience | 🔲 Planned |

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose**
- **Git**
- **AWS Account** (for S3 storage)
- **Stripe Account** (for payments)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/ETXSVC/buildersstream.git
cd buildersstream

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker compose up -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create demo organization & seed data
docker compose exec web python manage.py create_demo_org

# 6. Start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Access

- **API**: http://localhost:8000/api/v1/
- **Swagger UI**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/
- **Frontend**: http://localhost:5173/

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin / Owner | `admin@builderstream.com` | `demo1234!` |
| Project Manager | `pm@builderstream.com` | `demo1234!` |
| Estimator | `estimator@builderstream.com` | `demo1234!` |
| Field Worker | `field@builderstream.com` | `demo1234!` |
| Accountant | `accountant@builderstream.com` | `demo1234!` |
| Read Only | `readonly@builderstream.com` | `demo1234!` |

**Org**: Demo Construction Co. (`X-Organization-ID` in API headers)

---

## Configuration

### Environment Variables (.env)

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (use Docker service names)
DB_HOST=db
DB_NAME=builderstream
DB_USER=builderstream
DB_PASSWORD=builderstream

# Redis (use Docker service name)
REDIS_URL=redis://redis:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret
STRIPE_STARTER_PRICE_ID=price_xxx
STRIPE_PROFESSIONAL_PRICE_ID=price_xxx
STRIPE_ENTERPRISE_PRICE_ID=price_xxx

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=buildersstream-files
AWS_S3_REGION_NAME=us-east-1

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_key
DEFAULT_FROM_EMAIL=noreply@buildersstream.com
```

---

## Development

### Key Commands

```bash
# Docker workflow (all Django commands via Docker)
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell
docker compose exec web python manage.py create_demo_org

# Tests
cd builderstream
python -m pytest                          # All tests
python -m pytest apps/accounts/tests/    # Specific app
python -m pytest -v --tb=short           # Verbose

# Frontend
cd frontend
npm run dev        # Dev server (http://localhost:5173)
npm run build      # Production build
npm run type-check # TypeScript check
npm run lint       # ESLint
```

### Settings Structure

```
config/settings/
├── base.py         # Shared settings, CELERY_BEAT_SCHEDULE, middleware
├── development.py  # Local overrides (DEBUG=True, console email)
└── production.py   # Production settings (S3, SES, security headers)
```

### Adding a New Section

Each section follows the same pattern:

1. **Models** — define in `apps/{app}/models.py`, extend `TenantModel`
2. **Migration** — `makemigrations`, write manual migrations for complex changes
3. **Services** — business logic in `apps/{app}/services.py`
4. **Serializers** — in `apps/{app}/serializers.py` (List / Detail / Create patterns)
5. **Views** — `ModelViewSet` with `TenantViewSetMixin` in `apps/{app}/views.py`
6. **URLs** — register router in `apps/{app}/urls.py`, include in `config/urls.py`
7. **Signals** — side effects in `apps/{app}/signals.py`, register in `apps.py`
8. **Tasks** — Celery tasks in `apps/{app}/tasks.py`, add to `CELERY_BEAT_SCHEDULE`
9. **Admin** — register models in `apps/{app}/admin.py`
10. **Tests** — `apps/{app}/tests/` (conftest + test_models + test_services + test_views)

---

## Pricing Tiers

| Tier | Price/User/Month | Users | Features |
|------|-----------------|-------|----------|
| **Starter** | $15 | Up to 5 | Core + CRM + Basic Estimating |
| **Professional** | $50 | Up to 25 | All modules except Payroll |
| **Enterprise** | $125 | Unlimited | All modules + API + Premium support |

Annual discount: 20% off

---

## License

This project is **Confidential** and proprietary. All rights reserved.

---

## Links

- **Repo**: https://github.com/ETXSVC/buildersstream
- **Master Spec**: `Documentation/builders_prompt.md`

---

*Last Updated: February 2026*
