# Phase 16: Post-Project — Warranties, Service & Payroll

**Time required:** ~15 minutes
**Where you start:** Various sections
**Prerequisite:** Project is Paid / Complete
**Goal:** Register a workmanship warranty, handle a service request from the client, and run payroll for the project workers.

---

## Why This Step Matters

The job doesn't end when the check clears. Warranties protect the client and define your liability period. Service requests during the warranty period need to be tracked so they don't fall through the cracks. And your crew needs to be paid — the payroll run pulls from approved time entries and calculates wages automatically.

---

## Part A — Register a Workmanship Warranty

### Step 1 — Navigate to Service

1. In the left sidebar, click **Operations**.
2. In the sub-nav bar at the top, click **Service**.

**✅ You should see:** Three tabs: **Service Requests**, **Warranties**, **Warranty Claims** and four KPI cards: Open Requests, High Priority, Active Warranties, Open Claims.

### Step 2 — Go to Warranties Tab

1. Click the **Warranties** tab.

### Step 3 — Create a New Warranty

1. Click **+ New Warranty**.

**✅ You should see:** A modal titled **"New Warranty"**.

### Step 4 — Fill In Warranty Details

| Field | Value |
|---|---|
| Item Description * | Workmanship warranty — master bathroom tile, plumbing, and fixtures |
| Warranty Type | Workmanship |
| Status | Active |
| Project | Master Bath Remodel – Johnson |
| Provider | (your company name) |
| Start Date * | (today — project completion date) |
| Expiry Date * | (today + 1 year) |

### Step 5 — Save

1. Click **Create Warranty**.

**✅ Result:** Warranty appears in the warranties table. **Active Warranties** KPI card increases. Expiry date is clearly visible so you'll know when it lapses.

---

## Part B — Handle a Service Request (Warranty Claim)

### Scenario

Two weeks after project completion, Mike Johnson calls. One of the grout lines in the shower is cracking. This is a warranty issue — you need to track and resolve it.

### Step 1 — Create a Service Request

1. Click the **Service Requests** tab.
2. Click **+ New Request**.

**✅ You should see:** A modal titled **"New Service Request"**.

### Step 2 — Fill In the Request

| Field | Value |
|---|---|
| Title * | Grout cracking — master bath shower (warranty) |
| Description | Client reports a 4" crack developing in the grout joint between the shower niche and the adjacent wall tile. Appeared 2 weeks after project completion. Possible cause: minor substrate movement. Warranty repair required. |
| Priority | Medium |
| Status | New |
| Project | Master Bath Remodel – Johnson |
| Scheduled Date | (three days from today) |
| Est. Hours | 2 |

### Step 3 — Save

1. Click **Create Request**.

**✅ Result:** Service request appears with an auto-generated request number. **Open Requests** KPI card increases.

### Step 4 — Resolve the Service Request

After the repair is made:

1. Hover → Edit the service request.

| Field | Value |
|---|---|
| Status | Completed |

2. Save.

**✅ Result:** Service request status shows "Completed." **Open Requests** KPI card decreases.

---

## Part C — Run Payroll for the Project

### Step 1 — Navigate to Payroll

1. In the left sidebar, click **Finance & HR**.
2. In the sub-nav bar, click **Payroll**.

**✅ You should see:** Four tabs: **Pay Runs**, **Certified Payroll**, **Employees & Contractors**, **Workforce Summary** and four KPI cards: Active Employees, Contractors, Pending Pay Runs, Last Payroll Net.

### Step 2 — Verify Workers Exist

1. Click the **Employees & Contractors** tab.
2. Confirm the workers who logged time on this project appear in the list.
3. If no workers exist, click **+ Add Employee / Contractor** and add one:

| Field | Value |
|---|---|
| First Name * | James |
| Last Name * | Rivera |
| Email | james.rivera@yourcompany.com |
| Phone | (555) 340-2200 |
| Employment Type * | W-2 Full Time |
| Trade * | Finish Carpentry |
| Hire Date * | (one year ago) |
| Base Hourly Rate ($) * | 32.50 |

Click **Create Employee**.

### Step 3 — Create a Pay Run

1. Click the **Pay Runs** tab.
2. Click **+ New Pay Run**.

**✅ You should see:** A modal titled **"New Pay Run"** with an info banner explaining that it will calculate wages for all approved time entries in the period.

### Step 4 — Fill In Pay Run Details

| Field | Value |
|---|---|
| Period Start * | (Monday of the work week — e.g., last Monday) |
| Period End * | (Sunday of the work week — e.g., last Sunday) |
| Pay Date | (this Friday) |

### Step 5 — Create

1. Click **Create Pay Run**.

**✅ Result:** A new pay run appears in the table with status "Pending" showing the pay period dates, worker count, regular hours, overtime hours, and gross/net pay calculated from approved time entries.

### Step 6 — Process the Pay Run

1. Hover → click **Process** action on the pay run.

**✅ Result:** Status changes from "Pending" to "Processing" or "Approved."

### Step 7 — Approve and Mark Paid

1. Hover → click **Approve** (if available after processing).
2. Then hover → click **Mark Paid**.

**✅ You should see:** A confirmation modal titled **"Mark Pay Run as Paid"** showing the net pay amount and a **Payment Date** field.

| Field | Value |
|---|---|
| Payment Date * | (today) |

3. Click **Confirm Payment**.

**✅ Result:** Pay run status shows "Paid." **Last Payroll Net** KPI card updates to reflect this pay run.

---

## Part D — Final Project Audit

Do a final check across all modules to confirm everything is clean:

| Area | Check |
|---|---|
| **Projects** | Status = "Paid / Complete" |
| **CRM** | Lead for Mike Johnson = "Won" |
| **Scheduling** | All 7 tasks = "Completed" at 100% |
| **Field Ops** | All time entries = "Approved"; expenses = "Approved" |
| **Quality & Safety** | Final inspection = "Passed" (score 97) |
| **Documents** | RFI answered; submittal approved |
| **Financials** | All invoices = "Paid"; outstanding = $0 |
| **Service** | Warranty active; service request resolved |
| **Payroll** | Pay run = "Paid" |

---

## Verification Checklist

- [ ] Workmanship warranty exists with status "Active" and 1-year expiry
- [ ] Service request for grout crack exists with status "Completed"
- [ ] **Active Warranties** KPI card shows at least 1
- [ ] **Open Requests** KPI card shows 0
- [ ] Pay run exists with status "Paid"
- [ ] **Last Payroll Net** KPI card shows a dollar amount

---

## Common Issues

| Problem | What to do |
|---|---|
| Pay run shows $0 wages | Time entries for the period must be in "Approved" status — go approve them in Field Ops |
| No workers on pay run | Workers must be added as employees in the Employees & Contractors tab |
| Pay run can't be processed | Some pay runs require at least one time entry in the period — add a manual entry if needed |
| Warranty expiry date in the past | Double-check the expiry year — should be today + 1 year, not today + 1 day |

---

## Congratulations!

You have now completed the full BuilderStream workflow end-to-end:

```
Contact ✓ → Lead ✓ → Pipeline ✓ → Estimate ✓ → Proposal ✓ →
Project ✓ → Schedule ✓ → Field Ops ✓ → Q&S ✓ → Documents ✓ →
Invoices ✓ → Closeout ✓ → Payment ✓ → Warranty ✓ → Payroll ✓
```

The Mike Johnson master bath remodel has gone from first contact to paid project, fully documented in BuilderStream.
