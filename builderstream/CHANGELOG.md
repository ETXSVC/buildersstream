# BuilderStream Changelog

All notable changes to BuilderStream are documented here.

Versioning follows **Semantic Versioning**: `MAJOR.MINOR.PATCH`
- **MAJOR** — breaking changes or complete platform overhauls
- **MINOR** — new features, new modules, significant UX additions (backwards-compatible)
- **PATCH** — bug fixes, copy changes, minor UI tweaks

---

## [3.2.0] — 2026-03-16

### Added
- **Clickable KPI Cards** — all 11 module dashboard pages now navigate to the relevant
  tab or apply the relevant filter when a KPI card is clicked. Affected pages: CRM,
  Projects, Financials, Field Ops, Estimating, Quality & Safety, Documents, Payroll,
  Service, Scheduling, Company.
- **Playwright E2E Test Suite** — 44 automated end-to-end tests covering auth, dashboard,
  CRM, projects, navigation, collaboration, financials, and field ops. All tests pass
  against the live site. Run with `cd frontend && npm run test:e2e`.
- **Human Test Guide** — `human-tests/` folder with 15 step-by-step manual test
  documents covering the complete lead-to-completion workflow.

### Fixed
- `CRMPage` pipeline stages were using `stagesData?.results` but the API returns an
  array directly — fixed to `stagesData ?? []`, resolving an empty stage board.
- `ProjectsPage` "Active" KPI card `onClick` was setting status filter to `'production'`
  (not a valid status value) — corrected to `'in_progress'`.

### Developer
- `frontend/package.json` test scripts now use `node_modules/.bin/playwright` to avoid
  conflicts with globally-installed Playwright binaries.
- `playwright.config.ts` — reduced workers to 2 and added 45 s timeout for stability
  when testing against the live remote site.

---

## [3.1.0] — 2026-03-15

### Added
- **Sidebar Refactor** — simplified to 8 top-level links with per-section sub-navigation.
- **Company Dashboard** — separate Employees and Contractors tabs with workforce KPIs.
- **New Direct Message Modal** — start a DM from the Team/Collaboration page.
- **Deterministic DM Channel Slugs** — fixed unique constraint error on DM channel creation.

---

## [3.0.0] — 2026-03-01

### Added
- Full client portal frontend (`/pay/:token`) — public invoice payment via Stripe.
- Issue Tracking module (6 models, SLA timers, escalation rules, `/api/v1/issue-tracking/`).
- Dunning Workflows (DunningRule + DunningEvent, daily Celery task, `/settings/dunning`).
- Custom Fields Engine (`apps.custom_fields`, GenericFK values, `/settings/custom-fields`).
- Multi-Currency support (CurrencyService + Open Exchange Rates).

### Changed
- Major release — consolidates all sprint 4 / phase 8–14 work.

---

## [2.0.0] — 2026-02-01

### Added
- Sprint 3: Threaded project comments, universal search, command palette (⌘K).
- Sprint 2: Kanban board, white-label branding (OrganizationBranding), notification bell.
- Sprint 1: ASGI/Channels, 2FA TOTP, audit logs, WebSocket notifications.
- Phase 4.2: Team Channels + DMs (`apps.collaboration` WebSocket).
- Phase 1.2: Gantt View (frappe-gantt + `TaskViewSet.update_dates`).

---

## [1.0.0] — 2026-01-01

### Added
- Initial platform release.
- 18 Django apps: core, tenants, accounts, billing, projects, crm, estimating,
  scheduling, financials, clients, documents, field_ops, quality_safety, payroll,
  service, analytics, issue_tracking, custom_fields.
- React 18 + TypeScript frontend with all 11 module pages.
- Multi-tenancy (row-level org isolation), JWT auth, Stripe billing.
- Docker Compose deployment with Apache2 reverse proxy + Let's Encrypt SSL.
