# Phase 10: Field Operations

**Time required:** ~10 minutes
**Where you start:** Left sidebar → Operations
**Prerequisite:** Project is In Progress, tasks have been created
**Goal:** Clock in, log a day's work, and submit a field expense.

---

## Why This Step Matters

Field Ops is where the physical work gets documented. Time entries feed directly into payroll calculations. Daily logs create a written record of what was accomplished each day — invaluable for dispute resolution and certified payroll compliance. Field expenses capture costs at the point of purchase so nothing gets missed at billing time.

---

## Navigation

1. In the left sidebar, click **Operations**.
2. You should land on the Field Ops page with a sub-navigation bar showing **Field Ops**, **Quality & Safety**, **Service**.
3. Make sure **Field Ops** is selected in the sub-nav.

**✅ You should see:** Four KPI cards (Time Entries, Total Hours, Daily Logs, Pending Expenses) and a **clock status banner** showing whether you're currently clocked in.

---

## Part A — Clock In

### Step 1 — Check Clock Status

Look at the clock status banner near the top of the page (just above or below the KPI cards). It shows either:
- "Not clocked in" with a **Clock In** button
- "Currently clocked in to [Project]" with a **Clock Out** button

### Step 2 — Clock In to the Project

1. Click **Clock In**.

**✅ You should see:** A small confirmation that you're now clocked in. The banner updates to show "Currently clocked in."

> **Note:** For testing, you can immediately clock out again (see Part B). A real clock-in session would last the work day.

---

## Part B — Clock Out

1. When the banner shows "Currently clocked in," click **Clock Out**.
2. A time entry is created automatically with your clock-in and clock-out times.

**✅ Result:** The **Time Entries** KPI card count increases by 1. The **Total Hours** KPI card shows additional hours.

---

## Part C — Add a Manual Time Entry

For times when someone forgot to clock in, or to log time from the previous day:

### Step 1 — Go to Time Entries Tab

1. Click the **Time Entries** tab (first of the three tabs below the KPI cards).

### Step 2 — Create a Manual Entry

1. Click **+ Manual Entry**.

**✅ You should see:** A modal titled **"Manual Time Entry"**.

### Step 3 — Fill in the Entry

| Field | Value |
|---|---|
| Project | Master Bath Remodel – Johnson |
| Clock In * | (yesterday at 7:00 AM — use the datetime picker) |
| Clock Out | (yesterday at 3:30 PM) |
| Notes | Demolition — removed old tile, shower pan, and vanity. Site clean and ready for rough work. |

### Step 4 — Save

1. Click **Create Entry** (or the equivalent button).

**✅ Result:** A new time entry appears in the table showing 8.5 hours for the project.

---

## Part D — Log a Daily Field Report

### Step 1 — Go to Daily Logs Tab

1. Click the **Daily Logs** tab.

### Step 2 — Create a New Log

1. Click **+ New Log**.

**✅ You should see:** A modal titled **"New Daily Log"**.

### Step 3 — Fill In the Log

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Log Date * | (today's date) |
| Manpower Count | 3 |
| Work Performed * | Completed demolition of master bathroom. Removed old tile from floor and shower walls (~280 sq ft). Removed shower pan, old vanity and mirror. Uncapped old plumbing. Site prepped and debris hauled. Ready for rough plumbing inspection tomorrow. |
| Delay Reason | None |

### Step 4 — Save

1. Click **Create Log**.

**✅ Result:** Daily log appears in the table with status "Draft." The **Daily Logs** KPI card count increases.

### Step 5 — Submit the Log for Approval

1. Hover over the log row.
2. Click **Submit** to send it for supervisor review.

**✅ Result:** Status changes from "Draft" to "Submitted."

---

## Part E — Log a Field Expense

### Step 1 — Go to Expenses Tab

1. Click the **Expenses** tab.

### Step 2 — Create a New Expense

1. Click **+ New Expense**.

**✅ You should see:** A modal titled **"New Expense"**.

### Step 3 — Fill In the Expense

| Field | Value |
|---|---|
| Project | Master Bath Remodel – Johnson |
| Category * | Materials |
| Date * | (today) |
| Description * | Backer board and tile adhesive — 3 sheets HardieBacker + 2 bags Mapei adhesive |
| Amount ($) * | 187.50 |
| Mileage | (leave blank — only needed for Fuel category) |

### Step 4 — Save

1. Click **Create Expense**.

**✅ Result:** Expense appears in the table with status "Pending." The **Pending Expenses** KPI card increases.

---

## Part F — Approve the Time Entry and Expense

As a manager reviewing field activity:

### Approve Time Entry

1. Go to **Time Entries** tab.
2. Hover over the time entry row.
3. Click **Approve**.

**✅ Result:** Status changes to "Approved."

### Approve Expense

1. Go to **Expenses** tab.
2. Hover over the expense row.
3. Click **Approve**.

**✅ Result:** Status changes to "Approved."

---

## Verification Checklist

- [ ] At least one time entry exists for the project with "Approved" status
- [ ] Daily log exists with "Submitted" status
- [ ] Expense of $187.50 exists with "Approved" status
- [ ] **Time Entries** KPI card shows 2+ entries
- [ ] **Total Hours** KPI card reflects logged hours
- [ ] **Daily Logs** KPI card shows at least 1
- [ ] **Pending Expenses** KPI card shows 0 (after approval)

---

## Common Issues

| Problem | What to do |
|---|---|
| Clock In button doesn't appear | You may already be clocked in — check the banner text |
| Time entry shows wrong hours | Clock in/out times may have AM/PM flipped — edit the entry |
| Daily log stuck in Draft | You need to hover and click Submit — it doesn't auto-submit |
| Expense approval not visible | Only managers/admins can approve — check your user role |

---

## What Comes Next

With work underway and time being logged, it's time to run quality inspections to ensure workmanship meets standards.

→ Continue to: **09-quality-safety.md**
