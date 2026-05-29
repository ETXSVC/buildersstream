# BuilderStream Pro v3.0 — Features Specification

**Version:** 3.0
**Status:** Feature-Complete
**Stack:** Django 5.x, React 18, PostgreSQL, Redis, Celery, AWS S3

---

## 1. Core Platform Architecture

### Multi-Tenancy
- **Isolation:** Row-level organization-based isolation using thread-local storage.
- **Context Resolution:** Automatic organization context resolution via `X-Organization-ID` header or user's last active organization.
- **Scoping:** `TenantManager` ensures queries are automatically scoped to the active organization unless explicitly unscoped (e.g., for cross-tenant Celery tasks).

### Authentication & Security
- **Identity:** Email-only login (no usernames) with JWT stored in HttpOnly cookies (`bs_access`, `bs_refresh`).
- **Two-Factor Authentication (2FA):** TOTP-based 2FA with backup codes via `django-allauth`.
- **OAuth:** Google and GitHub OAuth scaffolded via `django-allauth`.
- **Role-Based Access Control (RBAC):** Hierarchical roles:
  - Owner (7) > Admin (6) > Project Manager (5) > Estimator (4) > Accountant (3) > Field Worker (2) > Read Only (1).
- **Module Gating:** `HasModuleAccess` permissions to restrict features based on subscription plans.
- **Audit Logs:** Full audit trail of authentication events and data changes.
- **IP Whitelisting:** Per-organization IP allowlist enforcement for sensitive operations.

### Billing & Subscriptions
- **Integration:** Deep integration with Stripe for subscription management.
- **Plans:** Tiered access (Starter, Professional, Enterprise) with feature limits.
- **Metering:** Usage-based metering for projects, users, and storage.
- **Enforcement:** Middleware blocks access if subscriptions are not active or trialing; past-due orgs get read-only access.
- **Dunning Workflows:** Automated retry and escalation rules for failed payments (`DunningRule` + `DunningEvent`).
- **Client Payment Portal:** Tokenized public invoice payment page at `/pay/:token` using Stripe Checkout.

### Custom Fields Engine
- **Org-Scoped Definitions:** Admins define custom fields per module (Text, Number, Date, Select, Multi-select, Boolean).
- **Generic Values:** Values stored via `ContentType` GenericForeignKey, applicable to any model.
- **API:** Full CRUD at `/api/v1/custom-fields/`.

---

## 2. Project Command Center

### Lifecycle Management
- **State Machine:** Strict 10-stage project lifecycle:
  - *Lead → Prospect → Estimate → Proposal → Contract → Production → Punch List → Closeout → Completed (or Canceled).*
- **Stage-Gates:** Validation requirements for transitions (e.g., "Contract" requires a client and estimated value; "Production" requires a start date and team).
- **Auto-Numbering:** Sequential project numbers per org per year (`BSP-{YEAR}-{SEQ:03d}`).

### Health & Performance
- **Health Scoring:** Automated 0-100 score calculated hourly via Celery tasks.
  - **Budget Variance:** 40 points
  - **Schedule Variance:** 30 points
  - **Overdue Items:** 30 points
- **Action Items:** Auto-generated tasks for overdue projects and upcoming milestones.
- **Activity Stream:** Full event log per project and org-wide.

### Dashboard
- **Performance:** Redis-cached dashboard data (60s TTL) for instant loading.
- **Widgets (customizable per user):**
  - Project Metrics (Active/On-Hold/Completed, health distribution)
  - Financial Summary (Revenue/Costs/Budget utilization)
  - Schedule Overview (Milestones/Crew Availability)
  - Action Items (Top 20 priority tasks)
  - Activity Stream (Real-time entity updates)
- **Customization:** Per-user widget visibility and layout persisted to backend.

### Threaded Comments
- **Per-Project:** Nested comment threads on projects with @mention support.
- **Real-time:** WebSocket-powered live updates via Django Channels.

---

## 3. CRM & Lead Management

### Pipeline Management
- **Kanban Board:** Visual pipeline with 8 default stages (New Lead → Won/Lost).
- **Lead Scoring:** Automated 0-100 score based on:
  - Estimated Value (30pts), Urgency (20pts), Source Quality (20pts), Engagement Level (20pts), Response Time (10pts).

### Automation Engine
- **Triggers:** Stage changes, time delays, score changes, or inactivity.
- **Actions:** Auto-send emails, create tasks, or notify users.
- **Conversion:** One-click conversion from Lead to Project (preserves history, links client).

### Analytics
- Conversion rates, win/loss reasons, lead velocity, pipeline value.

---

## 4. Estimating & Takeoffs

### Estimation Tools
- **Models:** Comprehensive data structure for Cost Items, Assemblies, and Proposals.
- **Digital Takeoff:** Integration for measuring quantities from plans (Area, Linear, Count).
- **Exports:** PDF and Excel generation for client-facing estimates.

### Proposals
- **E-Signature:** Integrated digital signature workflows for proposal acceptance.
- **Versioning:** Track revisions and history of sent proposals.

---

## 5. Document & Photo Control

### File Management
- **Storage:** Secure AWS S3 storage with presigned URLs for direct browser uploads.
- **Versioning:** Immutable version chains. Uploading a new file supersedes the old one while keeping a history link.
- **Validation:** Strict MIME type validation for documents (PDF, Office, CAD) and photos.

### RFI (Request for Information) System
- **Auto-Numbering:** Sequential RFI numbers per project (e.g., RFI-001).
- **Routing:** Workflow for creation, assignment, answering, and distribution.
- **Notifications:** Email distribution to stakeholders when answers are posted.
- **Audit Trail:** Full activity logging for creation, updates, and closure.

### Submittals
- Full submittal log with review workflow, status tracking, and version control.

### Photo Intelligence
- **EXIF Extraction:** Auto-extracts "Taken At" timestamps and GPS coordinates.
- **Thumbnailing:** Server-side generation of optimized 400px thumbnails.
- **AI Tagging:** Automated categorization based on project phase and image content.

---

## 6. Client Collaboration Portal

### Client Access
- **Magic Links:** Passwordless, secure JWT access for clients via email links.
- **Scoped Views:** Clients only see data explicitly shared with them.

### Features
- **Selections:** Digital approval workflows for materials and finishes.
- **Progress:** View photo galleries and project status updates.
- **Messaging:** Direct communication channel with the contractor team.
- **Payment Portal:** Clients can pay invoices online via tokenized Stripe Checkout link.

---

## 7. Scheduling & Resource Management

### Scheduling Engine
- **CPM Algorithm:** Critical Path Method calculation for project timelines.
- **Gantt Charts:** Visual timeline management with drag-and-drop date editing (`frappe-gantt`).
- **Milestones:** Tracking of key dates and deliverables.

### Resource Allocation
- **Crew Management:** Assignment of crews to tasks with availability checking.
- **Equipment:** Tracking of equipment usage and depreciation (monthly Celery task).

---

## 8. Financial Management Suite

- **Job Costing:** Real-time tracking of actuals vs. budget with variance analysis.
- **Budget Line Items:** Granular cost breakdown by category, phase, and trade.
- **Change Orders:** Management of scope changes with budget and schedule impact.
- **Purchase Orders:** PO creation, approval workflow, and receipt tracking.
- **Invoicing:** AIA G702/G703 style invoicing with line items and retention.
- **Draw Schedules:** Progress billing tied to project milestones.
- **Accounts Payable/Receivable:** Aging reports, overdue alerts.
- **Cash Flow Forecasting:** Based on payment schedules and projected expenses.
- **QuickBooks / Xero Integration Hooks:** Sync-ready data structures for accounting exports.
- **Dunning:** Automated payment retry rules with configurable escalation.

---

## 9. Field Operations Hub

- **GPS Clock-In/Out:** Location-stamped time entries with geofencing enforcement.
- **Daily Logs:** Structured daily field reports (weather, manpower, work performed, equipment).
- **Expense Tracking:** Mobile receipt capture with category and project assignment.
- **Equipment Dispatch:** Field equipment assignment and utilization tracking.
- **Overtime Calculation:** Automated overtime detection (daily Celery task).
- **Auto Clock-Out:** End-of-day auto clock-out for open time entries.

---

## 10. Quality & Safety

- **Inspections:** Checklist-based inspection workflows with pass/fail items.
- **Deficiencies:** Punch-list style deficiency tracking with photo evidence and resolution workflow.
- **Incidents:** OSHA-compliant incident reporting with severity classification.
- **Safety Observations:** Near-miss and hazard reporting.
- **Weekly Safety Reports:** Auto-generated Celery task every Monday.
- **Certification Tracking:** Worker certifications with expiry alerts.

---

## 11. Payroll & Workforce

- **Pay Periods:** Configurable weekly/bi-weekly/semi-monthly periods.
- **Timesheets:** Employee timesheet review and approval workflow.
- **Certified Payroll:** Davis-Bacon Act compliant certified payroll report generation.
- **Prevailing Wage Compliance:** Weekly compliance check Celery task.
- **Workforce Analytics:** Labor cost by project, trade, and time period.

---

## 12. Service & Warranty Management

- **Service Tickets:** Customer-facing ticket creation with priority and SLA.
- **Dispatch Board:** Technician assignment and scheduling.
- **SLA Tracking:** Response and resolution time monitoring with breach alerts.
- **Warranty Records:** Warranty terms, expiry tracking, and renewal alerts.
- **Recurring Service Agreements:** Auto-generated recurring invoices.

---

## 13. Analytics & Reporting Engine

- **KPI Engine:** Configurable key performance indicators calculated via Celery.
- **Report Builder:** Custom cross-project reports with filter/group/aggregate.
- **Scheduled Reports:** Email delivery of saved reports on a schedule.
- **Exports:** Excel and PDF export for all reports.
- **Weekly Summary:** Auto-generated executive summary every Monday.

---

## 14. Integrations

- **QuickBooks Online:** OAuth2 token exchange and sync hooks.
- **Xero:** Integration hooks for accounting data export.
- **Public API Keys:** Per-org API key management for third-party integrations.
- **Webhooks:** Outbound webhooks on configurable events.
- **Weather API:** Automatic weather data fetch for project locations (3-hour Celery task).

---

## 15. Issue Tracking

- **Issues:** Bug/task/feature tracking with priority, status, and assignee.
- **SLA Timers:** Configurable SLA rules with automatic breach detection (15-min Celery task).
- **Escalation Rules:** Auto-escalate issues based on SLA breach conditions.
- **Canned Responses:** Pre-written response templates for common issues.
- **Warning Notifications:** 30-min advance SLA breach warnings.

---

## 16. Platform Features (Sprints)

### Real-Time & WebSockets
- **Django Channels / ASGI:** Full async request handling via Daphne.
- **WebSocket Notifications:** Live in-app notification bell with unread count.
- **Team Channels:** Real-time team chat channels per organization.
- **Direct Messages:** Private one-to-one DM between team members.

### UX & Productivity
- **Universal Search:** Cross-module full-text search across projects, contacts, documents, and issues.
- **Command Palette (⌘K):** Keyboard-driven quick-action launcher.
- **White-Label Branding:** Per-org logo, colors, and custom CSS — live updates without reload.
- **Notification Bell:** Real-time unread count with categorized notification feed.

### Multi-Currency
- **Exchange Rates:** Live currency conversion via Open Exchange Rates API.
- **Per-Org Currency:** All financial figures stored and displayed in org's base currency.

### Mobile / PWA
- **Service Worker:** Offline-capable progressive web app.
- **Offline Sync:** Queue mutations locally and sync when connectivity resumes.
- **Geofencing:** Location-based clock-in/out enforcement on mobile.
- **Responsive Layouts:** Separate desktop, tablet, and mobile layout components.

---

## Technical Specifications

### API
- **Standard:** RESTful API via Django REST Framework.
- **Documentation:** OpenAPI/Swagger auto-generated docs at `/api/docs/`.
- **Performance:** Redis caching for high-read endpoints (Dashboard, Public Content).
- **Versioning:** All endpoints under `/api/v1/`.

### Background Processing
- **Engine:** Celery + Redis (broker on db 0, cache on db 1, channels on db 2).
- **Scheduler:** `django-celery-beat` with database-driven dynamic schedules.
- **Key Tasks:** Health scoring (hourly), lead automations (15min), SLA checks (15min), weather fetch (3h), dunning (daily 8am), certified payroll compliance (weekly).

### Frontend
- **Framework:** React 18 + TypeScript + Vite.
- **State:** Zustand (auth/org context) + React Query (server state).
- **Styling:** TailwindCSS with CSS custom property theming.
- **Charts:** Recharts for financial and analytics visualizations.
- **Gantt:** `frappe-gantt` with custom React wrapper.
