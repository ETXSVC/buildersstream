# BuilderStream Pro v3.0 — Detailed Features Specification

**Version:** 3.0
**Status:** Active Development (Sections 1-10 Complete)
**Stack:** Django 5.x, React 18, PostgreSQL, Redis, Celery, AWS S3

---

## 1. Core Platform Architecture

### Multi-Tenancy
- **Isolation:** Row-level organization-based isolation using thread-local storage.
- **Context Resolution:** Automatic organization context resolution via `X-Organization-ID` header or user's last active organization.
- **Scoping:** `TenantManager` ensures queries are automatically scoped to the active organization unless explicitly unscoped (e.g., for cross-tenant Celery tasks).

### Authentication & Security
- **Identity:** Email-only login (no usernames) with JWT (JSON Web Token) authentication.
- **Role-Based Access Control (RBAC):** Hierarchical roles:
  - Owner (7) > Admin (6) > Project Manager (5) > Estimator (4) > Accountant (3) > Field Worker (2) > Read Only (1).
- **Module Gating:** `HasModuleAccess` permissions to restrict features based on subscription plans.

### Billing & Subscriptions
- **Integration:** Deep integration with Stripe for subscription management.
- **Plans:** Tiered access (Starter, Professional, Enterprise) with feature limits.
- **Metering:** Usage-based metering for projects, users, and storage.
- **Enforcement:** Middleware blocks access if subscriptions are not active or trialing.

---

## 2. Project Command Center

### Lifecycle Management
- **State Machine:** Strict 10-stage project lifecycle:
  - *Lead → Prospect → Estimate → Proposal → Contract → Production → Punch List → Closeout → Completed (or Canceled).*
- **Stage-Gates:** Validation requirements for transitions (e.g., "Contract" requires a client and estimated value; "Production" requires a start date and team).

### Health & Performance
- **Health Scoring:** Automated 0-100 score calculated hourly via Celery tasks.
  - **Budget Variance:** 40 points
  - **Schedule Variance:** 30 points
  - **Overdue Items:** 30 points
- **Action Items:** Auto-generated tasks for overdue projects and upcoming milestones.

### Dashboard
- **Performance:** Redis-cached dashboard data (60s TTL) for instant loading.
- **Widgets:**
  - Project Metrics (Active/On-Hold/Completed)
  - Financial Summary (Revenue/Costs/Budget)
  - Schedule Overview (Milestones/Crew Availability)
  - Activity Stream (Real-time entity updates)

---

## 3. CRM & Lead Management

### Pipeline Management
- **Kanban Board:** Visual pipeline with 8 default stages (New Lead → Won/Lost).
- **Lead Scoring:** Automated 0-100 score based on:
  - Estimated Value (30pts)
  - Urgency (20pts)
  - Source Quality (20pts)
  - Engagement Level (20pts)
  - Response Time (10pts)

### Automation Engine
- **Triggers:** Stage changes, time delays, score changes, or inactivity.
- **Actions:** Auto-send emails, create tasks, or notify users.
- **Conversion:** One-click conversion from Lead to Project (preserves history, links client).

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

### Photo Intelligence
- **EXIF Extraction:** Auto-extracts "Taken At" timestamps and GPS coordinates (Latitude/Longitude).
- **Thumbnailing:** Server-side generation of optimized 400px thumbnails.
- **AI Tagging:** Automated categorization based on project phase (e.g., "Pre-Construction", "Punch-List") and image content.

---

## 6. Client Collaboration Portal

### Client Access
- **Magic Links:** Passwordless, secure JWT access for clients via email links.
- **Scoped Views:** Clients only see data explicitly shared with them.

### Features
- **Selections:** Digital approval workflows for materials and finishes.
- **Progress:** View photo galleries and project status updates.
- **Messaging:** Direct communication channel with the contractor team.

---

## 7. Scheduling & Resource Management

### Scheduling Engine
- **CPM Algorithm:** Critical Path Method calculation for project timelines.
- **Gantt Charts:** Visual timeline management with dependencies.
- **Milestones:** Tracking of key dates and deliverables.

### Resource Allocation
- **Crew Management:** Assignment of crews to tasks with availability checking.
- **Equipment:** Tracking of equipment usage and depreciation.

---

## 8. Financial Management Suite (In Progress)

*Note: This section is currently the active development focus (Section 11).*

- **Job Costing:** Real-time tracking of actuals vs. budget.
- **Invoicing:** AIA G702/G703 style invoicing support.
- **Change Orders:** Management of scope changes and budget impacts.
- **Cash Flow:** Forecasting based on payment schedules and expenses.

---

## 9. Future Modules (Planned)

### Field Operations Hub
- Daily logs, time tracking, and GPS geofencing.

### Quality & Safety
- Inspections, incident reporting, and OSHA compliance forms.

### Payroll & Workforce
- Timesheets, certified payroll, and workforce management.

### Analytics Engine
- Custom report builders and cross-project analytics.

---

## Technical Specifications

### API
- **Standard:** RESTful API via Django REST Framework.
- **Documentation:** OpenAPI/Swagger auto-generated docs.
- **Performance:** Redis caching for high-read endpoints (Dashboard, Public Content).

### Background Processing
- **Engine:** Celery + Redis.
- **Tasks:** Scheduled jobs for health scoring (hourly), lead automations (15min), and usage metering.