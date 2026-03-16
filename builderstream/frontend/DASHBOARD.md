# Dashboard & Module Dashboards

BuilderStream has two tiers of dashboards:

1. **Home Dashboard** (`/`) — org-wide summary with 5 widgets
2. **Module Dashboards** — each section page has KPI cards + charts at the top

---

## Home Dashboard

Located at `frontend/src/features/dashboard/`.

### Widgets

| Widget | Description |
|--------|-------------|
| `ProjectMetricsWidget` | Project overview with health distribution |
| `FinancialSummaryWidget` | Budget, revenue, costs |
| `ScheduleOverviewWidget` | Milestones and crew availability |
| `ActionItemsWidget` | Top 20 priority action items |
| `ActivityStreamWidget` | Recent project activity feed |

### API Endpoints
- `GET /api/v1/dashboard/` — cached org dashboard (60s Redis TTL)
- `GET /api/v1/dashboard/layout/` — user's widget visibility settings
- `PUT /api/v1/dashboard/layout/` — save widget customization

---

## Module Dashboards

Each section page shows KPI cards + Recharts charts above the data table/list.
All metrics are derived client-side from existing API hooks using `useMemo`.

### Shared Component

`frontend/src/components/KpiCard.tsx` — reusable KPI card with label, value, sub-text, and color accent variants (`default`, `green`, `red`, `amber`, `blue`, `indigo`).

### Per-Module Summary

| Module | KPIs | Charts |
|--------|------|--------|
| **Projects** | Total, Active, Pipeline Value, Health Red | Status bar + Health pie |
| **CRM** | Total Leads, Hot Leads, Pipeline Value, Contacts | Leads by stage bar + Urgency pie |
| **Financials** | Total Invoiced, Outstanding, Overdue, Expenses | Invoice status pie + count bar |
| **Scheduling** | Total Tasks, In Progress, Completed, Overdue | Status bar + distribution pie |
| **Field Ops** | Time Entries, Total Hours, Daily Logs, Pending Expenses | Log status pie + count bar |
| **Documents** | Documents, Open RFIs, Pending Submittals, Photos | RFI status pie + Submittals bar |
| **Estimating** | Total Estimates, Approved, Est. Value, Win Rate | Status bar + mix pie |
| **Quality & Safety** | Inspections, Pass Rate, Open Deficiencies, Incidents | Inspection results pie + Severity bar |
| **Service** | Open Requests, High Priority, Active Warranties, Open Claims | Status bar + Priority pie |
| **Payroll** | Active Employees, Contractors, Pending Pay Runs, Last Payroll Net | Employment type pie + Trade bar |
| **Issues** | Open Issues, Critical, SLA Compliance, Resolved | Status bar + Priority pie |

### Charting Library

[Recharts](https://recharts.org/) v3 — `BarChart`, `PieChart`, `ResponsiveContainer`, `Cell`, `Legend`, `Tooltip`.

---

## Tech Stack

- **React 18** — UI framework
- **TypeScript** — Type safety
- **TailwindCSS** — Styling
- **React Query (@tanstack/react-query)** — Data fetching & caching
- **Recharts** — Charts and visualizations
- **Zustand** — Auth state
- **Axios** — HTTP client
- **Vite** — Build tool

---

## Running

```bash
cd frontend
npm install
npm run dev      # dev server at http://localhost:5173
npm run build    # production build to dist/
```

Login: `admin@builderstream.com` / `demo1234!`
