# BuilderStream — Marketing vs. Implementation Gap Report

**Generated:** 2026-03-19
**Scope:** `buildersstream.online` marketing site vs. `/var/www/builderstream/builderstream` codebase

---

## Executive Summary

The core construction management platform is **substantially complete and accurate** in its marketing.
All 19 Django apps are functional, all 11 module pages are wired in the frontend, and 74 E2E tests pass.

However, five categories of delta exist:

| Category | Severity | Count |
|---|---|---|
| Stub integrations marketed as real | HIGH | 6 |
| Pricing tier limits not enforced | MEDIUM | 3 |
| Enterprise features not built | MEDIUM | 2 |
| Underpromoted completed features | LOW | 15 |
| Minor copy inaccuracies | LOW | 3 |

---

## 1. CRITICAL GAPS — Marketing Claims That Are Not Implemented

### 1.1 Third-Party Integrations (Features Page)

The Features page (`Features.tsx:32`) displays logos/badges for:

> "Integrates With: **QuickBooks, Gmail, Outlook, Slack, Zoom, Dropbox**"

**Reality:**

| Integration | Status | Evidence |
|---|---|---|
| QuickBooks Online | **STUB** | `apps/financials/services.py:548` — `QuickBooksSyncService` returns `{"status": "stub"}` on all methods |
| QuickBooks Desktop | **STUB** | Same service, no QBD-specific code |
| Xero | **STUB** | Referenced in service docstring as "Phase 2 feature" |
| Gmail | **NOT EXISTS** | Zero integration code in any app |
| Outlook / Microsoft 365 | **NOT EXISTS** | Zero integration code in any app |
| Slack | **NOT EXISTS** | Zero integration code in any app |
| Zoom | **NOT EXISTS** | Zero integration code in any app |
| Dropbox | **NOT EXISTS** | Zero integration code in any app |

**What IS integrated:**
- Stripe (billing, client payment portal) — fully functional
- Open Exchange Rates (multi-currency) — functional
- SMTP/SES (transactional email) — functional
- Weather API (field ops, scheduling) — functional

---

### 1.2 Pricing Tier Limits Not Enforced

`Pricing.tsx` claims:
- **Starter:** "5 Active Projects" and "CRM (Up to 50 leads)"
- **Professional:** "Unlimited Projects" and "Unlimited CRM"

**Reality:** `apps/billing/models.py` has no `max_projects`, `max_leads`, or per-resource limit fields. `SubscriptionPlan` tracks `max_users` only. No middleware, permission class, or serializer enforces project/lead counts against any tier limit. A Starter subscriber can create unlimited projects today.

---

### 1.3 Mobile App (Pricing — Starter Tier)

Starter tier lists **"Mobile App Access"** as a feature.

**Reality:** There is no native iOS or Android app. The platform is a responsive React SPA (PWA-capable via service worker). The service worker exists (`frontend/public/sw.js`) but there is no app in any app store.

---

### 1.4 SSO & Advanced Security (Pricing — Enterprise Tier)

Enterprise tier claims **"SSO & Advanced Security"**.

**Reality:** No SAML 2.0 or OIDC/OAuth2 SSO implementation exists in `apps/accounts/`. Authentication is JWT (SimpleJWT) + email/password + 2FA TOTP. 2FA is well-implemented but is not SSO.

---

## 2. MEDIUM GAPS — Partially Implemented Features

### 2.1 AIA Progress Billing

Features page references AIA billing. `apps/financials/models.py:196` defines `PROGRESS = "progress", "Progress Billing (AIA G702)"` and the Invoice model has AIA fields (`scheduled_value`, `work_completed`, `stored_materials`). However:
- No AIA G702/G703 PDF generation found
- No AIA-specific serializer validation
- No frontend AIA billing form in `features/financials/`

**Status:** Data model present; UI and PDF output missing.

---

### 2.2 Forecasting Tools (Analytics)

Analytics module claims "forecasting tools". `apps/analytics/` has `ReportTemplate` and `ReportExecution` models with a report builder. No cash-flow forecast, revenue projection, or predictive models found.

**Status:** General reporting exists; forward-looking forecasting does not.

---

### 2.3 Delay Impact Analysis (Scheduling)

Features page mentions auto-adjusting dependent tasks on delays. Task dependencies exist in the `scheduling` app but no cascade-update logic was found in services. Manual date changes via Gantt are supported; automatic propagation is not.

---

## 3. UNDERPROMOTED FEATURES — Built But Not Marketed

The following are **fully implemented** in the codebase but receive no mention on the marketing site:

| Feature | Location | Value Proposition |
|---|---|---|
| Kanban Board | `features/projects/KanbanPage.tsx` | Visual project pipeline management |
| Issue Tracking + SLA Timers | `apps/issue_tracking/` | 6 models, escalation rules, SLA enforcement |
| Threaded Project Comments | `features/projects/ProjectComments.tsx` | In-context collaboration per project |
| Custom Fields Engine | `apps/custom_fields/` | Org-scoped fields on any model (GenericFK) |
| Multi-Currency Support | `apps/financials/services.py → CurrencyService` | Open Exchange Rates integration |
| White-Label Branding | `apps/tenants/models.py → OrganizationBranding` | Custom logo, colors, subdomain per org |
| 2FA / TOTP | `apps/accounts/` | Two-factor authentication via authenticator app |
| Command Palette (⌘K) | `features/` | Universal keyboard-driven search |
| Universal Search | Implemented in backend + frontend | Cross-module full-text search |
| Team Messaging + DMs | `apps/collaboration/` | WebSocket channels, private DMs, archive/restore |
| Dunning Workflows | `apps/billing/ → DunningRule` | Automated payment retry and overdue notices |
| Client Payment Portal | `/pay/:token` | Magic-link Stripe payment for client invoices |
| PWA / Offline Sync | `frontend/public/sw.js` | Service worker for offline capability |
| Audit Logs | `ActivityLog` across apps | Full activity trail per org |
| Role-Based Access Control | `apps/tenants/permissions.py` | 7-tier RBAC (owner → read_only) |

---

## 4. MINOR COPY INACCURACIES

| Page | Claim | Reality |
|---|---|---|
| Features page | "Plan markup tools" | `annotations` JSONField exists on Photo model for canvas-based markup — implemented in data layer; frontend draw tooling not confirmed |
| About page | "Join thousands of contractors" | Platform is in beta; no usage metrics available |
| Footer | `hello@buildersstream.pro` | Domain `.pro` vs `.online` — possible misdirected email |

---

## Summary Matrix

| Gap | Severity | Effort to Fix | Priority |
|---|---|---|---|
| Slack integration | HIGH | Large | P1 |
| QuickBooks integration | HIGH | Large | P1 |
| Pricing tier enforcement | MEDIUM | Medium | P2 |
| SSO (Enterprise) | MEDIUM | Large | P3 |
| AIA G702/G703 PDF output | MEDIUM | Medium | P2 |
| Forecasting module | MEDIUM | Large | P3 |
| Delay cascade scheduling | LOW | Medium | P3 |
| Gmail/Outlook/Zoom/Dropbox | HIGH | Large | P4 (or remove claim) |
| Mobile app (native) | HIGH | Very Large | P4 (or reframe as PWA) |
| Marketing underpromoted features | LOW | Small (copy only) | P1 |
| Footer email domain | LOW | Trivial | P1 |
