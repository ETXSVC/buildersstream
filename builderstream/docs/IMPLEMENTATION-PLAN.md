# BuilderStream — Gap Implementation Plan

**Created:** 2026-03-19
**Source:** `docs/GAP-REPORT.md`
**Approach:** Address gaps in priority order. Each sprint below is independent and shippable.

---

## Sprint A — Quick Wins: Marketing Accuracy (1–2 days)

These require no backend code — only copy/UI changes to the marketing website.

### A1 — Fix Integration Claims on Features Page

**File:** `/var/www/builderstream/website/src/pages/Features.tsx`

Replace the false integration badge list with accurate claims:

- **Remove:** QuickBooks, Gmail, Outlook, Slack, Zoom, Dropbox badges
- **Add:** Stripe, Open Exchange Rates (multi-currency), Weather API, Email (SMTP/SES)
- **Add "Coming Soon" section** with QB Online, Xero, Google Workspace, Slack — honest roadmap framing

**Effort:** 1 hour

---

### A2 — Reframe "Mobile App" as PWA

**File:** `Pricing.tsx` Starter tier features list

Change `"Mobile App Access"` → `"Mobile-Optimized PWA"` or `"Works on Any Device"`.

Optionally add a PWA section to the Features page: install prompt, offline support, home screen icon.

**Effort:** 30 minutes

---

### A3 — Fix Footer Email Domain

**File:** `Footer.tsx`

Change `hello@buildersstream.pro` → `hello@buildersstream.online` (matches the live domain).

**Effort:** 5 minutes

---

### A4 — Add Underpromoted Features to Website

Update `Features.tsx` to include modules that are fully built but not marketed:

| Add to Features Page | Existing Code Location |
|---|---|
| Kanban Board | `features/projects/KanbanPage.tsx` |
| Issue Tracking + SLA | `apps/issue_tracking/` |
| Custom Fields Engine | `apps/custom_fields/` |
| Team Messaging + Channels | `apps/collaboration/` |
| 2FA / TOTP Security | `apps/accounts/` |
| Multi-Currency Support | `apps/financials/ → CurrencyService` |
| White-Label Branding | `apps/tenants/ → OrganizationBranding` |
| Dunning Workflows | `apps/billing/ → DunningRule` |
| Client Payment Portal | `/pay/:token` |

**Effort:** 2–3 hours (copy + ModuleCard entries)

---

## Sprint B — Pricing Tier Enforcement (3–5 days)

Implement hard limits that match what `Pricing.tsx` advertises.

### B1 — Add Limit Fields to SubscriptionPlan

**File:** `apps/billing/models.py`

```python
class SubscriptionPlan(models.Model):
    # ... existing fields ...
    max_projects = models.PositiveIntegerField(null=True, blank=True)   # null = unlimited
    max_crm_leads = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited
    max_crm_contacts = models.PositiveIntegerField(null=True, blank=True)
    has_api_access = models.BooleanField(default=False)
    has_sso = models.BooleanField(default=False)
    has_custom_reporting = models.BooleanField(default=False)
    has_white_label = models.BooleanField(default=False)
```

Seed data for each tier:

| Tier | max_projects | max_crm_leads | has_api_access |
|---|---|---|---|
| Starter | 25 | 100 | False |
| Professional | None (unlimited) | None | False |
| Enterprise | None | None | True |

**Migration:** `apps/billing/migrations/00XX_subscriptionplan_limits.py`

---

### B2 — Limit Enforcement in API Layer

**File:** `apps/projects/views.py` — `ProjectViewSet.perform_create()`

```python
def perform_create(self, serializer):
    org = self.request.organization
    plan = org.subscription.plan
    if plan.max_projects is not None:
        active_count = Project.objects.for_organization(org).exclude(
            status='canceled'
        ).count()
        if active_count >= plan.max_projects:
            raise ValidationError(
                f"Your plan allows a maximum of {plan.max_projects} active projects. "
                "Upgrade to Professional to create more."
            )
    serializer.save(organization=org)
```

Apply same pattern in `apps/crm/views.py → LeadViewSet.perform_create()` for `max_crm_leads`.

---

### B3 — API Access Gate

**File:** `apps/tenants/permissions.py`

Add `HasApiAccess` permission class:

```python
class HasApiAccess(BasePermission):
    def has_permission(self, request, view):
        org = getattr(request, 'organization', None)
        if not org:
            return False
        plan = org.subscription.plan
        return plan.has_api_access
```

Apply to any public API key endpoints.

---

### B4 — Frontend Upgrade Prompt

When a limit is hit, the API returns `402 Payment Required` with a structured error body. Frontend should intercept this and show an upgrade modal rather than a generic error toast.

**File:** `frontend/src/api/client.ts` — add 402 interceptor that dispatches an `upgrade-required` event caught by a global `UpgradeModal` component.

---

## Sprint C — AIA G702/G703 Billing (3–5 days)

Complete the partially-built AIA billing feature.

### C1 — AIA Invoice Serializer

**File:** `apps/financials/serializers.py`

Add `AIAInvoiceSerializer` that validates and computes:
- `scheduled_value` (original contract amount)
- `work_completed_from_previous` (sum of prior applications)
- `work_completed_this_period`
- `stored_materials`
- `total_completed_and_stored` (computed)
- `retainage_percent` + `retainage_amount` (computed)
- `net_payment_due` (computed)

---

### C2 — AIA PDF Generation

**File:** `apps/financials/services.py`

```python
class AIABillingService:
    @staticmethod
    def generate_g702(invoice: Invoice) -> bytes:
        """Generate AIA G702 Application for Payment PDF."""
        # Use reportlab or weasyprint
        # Returns PDF bytes — caller saves to DocumentFile or streams as response
        ...

    @staticmethod
    def generate_g703(invoice: Invoice) -> bytes:
        """Generate AIA G703 Continuation Sheet PDF."""
        ...
```

**Endpoint:** `POST /api/v1/financials/invoices/{pk}/generate-aia/` returns PDF download.

---

### C3 — Frontend AIA Form

**File:** `frontend/src/features/financials/`

Add "AIA Billing" tab to the Invoice detail page. Show the G702 fields in a structured form matching the standard paper form layout. "Generate PDF" button calls the endpoint and triggers download.

---

## Sprint D — QuickBooks Integration (5–10 days)

Complete the existing stub in `apps/financials/services.py:QuickBooksSyncService`.

### D1 — OAuth 2.0 Flow

QuickBooks Online uses OAuth 2.0 with PKCE. Required endpoints:

- `GET /api/v1/integrations/qbo/connect/` — initiate OAuth, redirect to Intuit
- `GET /api/v1/integrations/qbo/callback/` — receive code, exchange for tokens, store in `QBOConnection` model

**New model:** `apps/integrations/models.py → QBOConnection(TenantModel)` storing `access_token`, `refresh_token`, `realm_id`, `token_expiry`.

---

### D2 — Sync Services

Replace stubs in `QuickBooksSyncService` with real `python-quickbooks` or direct REST calls:

```python
class QuickBooksSyncService:
    def push_invoice(self, invoice: Invoice) -> dict:
        conn = QBOConnection.objects.for_organization(self.org).first()
        qbo = QuickBooks(client_id=..., client_secret=...,
                         access_token=conn.access_token, realm_id=conn.realm_id)
        qb_invoice = Invoice.from_obj({...})
        return qb_invoice.save(qb=qbo)

    def pull_vendors(self) -> list:
        ...

    def push_expense(self, expense: Expense) -> dict:
        ...
```

---

### D3 — Celery Sync Task

```python
@shared_task(name="integrations.sync_qbo")
def sync_qbo(organization_id):
    """Hourly: push unpushed invoices/expenses to QuickBooks."""
    ...
```

---

### D4 — Frontend Integration Settings Page

**File:** `frontend/src/features/settings/`

Add "Integrations" tab to Settings. Show QuickBooks connection card with:
- Connect / Disconnect button
- Last sync timestamp
- Manual "Sync Now" button
- Sync error log

---

## Sprint E — Slack Integration (5–7 days)

Highest-value external integration for construction teams.

### E1 — Slack OAuth

New app: `apps/integrations/slack.py`

- `GET /api/v1/integrations/slack/connect/` — Slack OAuth install
- `GET /api/v1/integrations/slack/callback/` — store `SlackConnection(TenantModel)` with `bot_token`, `team_id`, `webhook_url`

---

### E2 — Notification Hooks

Trigger Slack messages for key events via `apps/projects/signals.py` and `apps/crm/signals.py`:

| Event | Slack Message |
|---|---|
| Project status changed | `#projects` channel |
| New lead created | `#crm` channel |
| Invoice overdue (dunning) | `#finance` channel |
| Safety incident reported | `#safety` channel |
| Daily log submitted | `#field` channel |

**Pattern:** Django signal → Celery task → `SlackNotificationService.send(channel, text, blocks)`

---

### E3 — Settings UI

Add Slack card to the Integrations settings tab (Sprint D4). Same connect/disconnect pattern.

---

## Sprint F — SSO (Enterprise Tier) (7–10 days)

### F1 — SAML 2.0 via `python3-saml`

**New model:** `SSOConfiguration(TenantModel)` with `idp_entity_id`, `idp_sso_url`, `idp_x509_cert`, `sp_acs_url`.

**Endpoints:**
- `GET /api/v1/auth/saml/metadata/` — SP metadata XML
- `POST /api/v1/auth/saml/acs/` — Assertion Consumer Service (receives IdP response)
- `GET /api/v1/auth/saml/login/` — initiate SSO redirect

**Flow:**
1. Enterprise org configures IdP (Okta, Azure AD, etc.) in Settings
2. User on `app.buildersstream.online/login` with SSO email → redirect to IdP
3. IdP returns SAML assertion → `acs/` validates → JWT issued → normal session

---

### F2 — Frontend SSO Login

**File:** `frontend/src/features/auth/LoginPage.tsx`

Add "Sign in with SSO" button. On click: POST `{email}` to `GET /api/v1/auth/saml/login/?email=...` to get the IdP redirect URL, then `window.location.href` to it.

---

## Sprint G — Forecasting Module (7–10 days)

### G1 — Cash Flow Forecast

**File:** `apps/analytics/services.py`

```python
class ForecastService:
    @staticmethod
    def cash_flow_forecast(org, months=12) -> list[dict]:
        """
        Project monthly cash in/out based on:
        - Active project timelines + % complete
        - Scheduled invoice due dates
        - Historical expense run-rate per active project
        - Pending change orders
        Returns list of {month, projected_in, projected_out, net, cumulative}
        """
```

---

### G2 — Revenue Forecast

Uses CRM pipeline + lead conversion probability:

```python
class ForecastService:
    @staticmethod
    def revenue_pipeline_forecast(org) -> dict:
        """
        Weighted pipeline value by stage probability.
        Each PipelineStage has win_probability (add field).
        Lead.estimated_value * stage.win_probability = weighted_value
        """
```

---

### G3 — Forecast API + Frontend

**Endpoint:** `GET /api/v1/analytics/forecast/` with `?type=cash_flow|revenue&months=3|6|12`

**Frontend:** New "Forecast" tab in the Analytics page. Two Recharts: AreaChart for cash flow over time, BarChart for pipeline weighted revenue by month.

---

## Sprint H — Scheduling Delay Cascade (2–3 days)

### H1 — Task Dependency Cascade Service

**File:** `apps/scheduling/services.py`

```python
class ScheduleCascadeService:
    @staticmethod
    def propagate_delay(task: Task, new_end_date: date):
        """
        When a task's end date moves, find all successor tasks
        (those with this task in their dependencies) and shift
        their start/end dates by the same delta, recursively.
        Uses topological sort to avoid cycles.
        """
```

Called from `TaskViewSet.update_dates()` action (already used by Gantt drag).

---

### H2 — Delay Impact Report

**Endpoint:** `GET /api/v1/scheduling/tasks/{pk}/delay-impact/`

Returns which downstream tasks would be affected, by how many days, and total schedule slip for the project.

**Frontend:** Show impact summary in a confirmation dialog before the user saves a Gantt drag that moves a task with dependents.

---

## Execution Order

```
Week 1:   Sprint A (marketing accuracy) — ship immediately, no code risk
Week 1:   Sprint B (pricing enforcement) — affects all new signups
Week 2:   Sprint C (AIA billing) — completes partially-built feature
Week 3-4: Sprint D (QuickBooks) — highest-value integration
Week 5:   Sprint E (Slack) — team communication integration
Week 6-7: Sprint F (SSO) — enterprise gate feature
Week 8-9: Sprint G (forecasting) — analytics value-add
Week 9:   Sprint H (delay cascade) — scheduling completeness
```

---

## Out of Scope (Remove from Marketing or Defer)

| Item | Recommendation |
|---|---|
| Gmail / Outlook integration | Remove from Features page. Add to "Roadmap" section. |
| Zoom integration | Remove from Features page. No clear construction use case. |
| Dropbox integration | Replace with "Local & Cloud Storage" — native storage already works. |
| Dedicated Success Manager | This is a people/ops function, not software. Keep on Pricing but note it's for Enterprise contracts. |
| "Thousands of contractors" copy | Change to "Built for construction teams" until usage data supports the claim. |
