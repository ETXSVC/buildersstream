# Phase 13: Financials — Invoices, Expenses & Change Orders

**Time required:** ~15 minutes
**Where you start:** Finance & HR → Financials
**Prerequisite:** Project is In Progress; RFI for the self-leveling compound was answered and approved
**Goal:** Create a progress invoice, log the approved change order, and track project expenses.

---

## Why This Step Matters

Cash flow is the lifeblood of construction. Progress billing keeps money coming in during the job. Change orders protect you from doing extra work for free. Expense tracking ensures every cost is captured and reconciled against the budget before the project closes.

---

## Navigation

1. In the left sidebar, click **Finance & HR**.
2. You should land on the Financials page with sub-nav showing **Financials** and **Payroll**.
3. Make sure **Financials** is selected.

**✅ You should see:** Five tabs: **Invoices**, **Expenses**, **Change Orders**, **Purchase Orders**, **Budgets** and four KPI cards: Total Invoiced, Outstanding, Overdue Invoices, Total Expenses.

---

## Part A — Create a Progress Invoice (Draw #1)

### Scenario

The rough work is complete (demo, rough plumbing, rough electrical). You're 35% through the project — time to bill the first progress draw.

35% of $45,000 = **$15,750**

### Step 1 — Go to Invoices Tab

1. Click the **Invoices** tab (should be the default).

### Step 2 — Create a New Invoice

1. Click **+ New Invoice**.

**✅ You should see:** A modal titled **"New Invoice"**.

### Step 3 — Fill In Invoice Details

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Status | Draft |
| Due Date | (today + 14 days) |

### Step 4 — Save

1. Click **Create Invoice**.

**✅ Result:** Invoice appears in the table with an auto-generated invoice number (e.g., INV-2026-001), status "Draft," and the project name. The invoice total may show $0 until line items are added.

> **Note:** Invoice line items are added through the invoice detail/edit view. After creating the invoice, you would edit it to add:
> - Progress Draw #1 — 35% completion: $15,750

### Step 5 — Mark Invoice as "Sent"

After adding line items and reviewing:

1. Hover over the invoice row → click **Edit**.
2. Change Status to **Sent**.
3. Save.

**✅ Result:** Invoice status shows "Sent." **Total Invoiced** KPI card increases to reflect the amount. **Outstanding** KPI card shows the unpaid balance.

---

## Part B — Create a Change Order (Self-Leveling Compound)

From the RFI that was answered in Phase 12, we need to document the $400 cost addition.

### Step 1 — Go to Change Orders Tab

1. Click the **Change Orders** tab.

**✅ You should see:** A table with columns: CO #, Project, Title, Amount, Status, Submitted.

### Step 2 — Create a New Change Order

1. Click **+ New Change Order**.

**✅ You should see:** A modal titled **"New Change Order"**.

### Step 3 — Fill In Change Order Details

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Title * | CO-001: Floor Self-Leveling Compound — NW Corner |
| Amount ($) | 400 |
| Status | Draft |
| Reason | Floor elevation discrepancy of 1.5" discovered in NW corner during tile layout (ref: RFI-001). Owner approved Option A: apply self-leveling compound to achieve flat surface. Includes materials ($220) and labor ($180). |

### Step 4 — Save

1. Click **Create Change Order**.

**✅ Result:** Change order appears with CO # (e.g., CO-001), amount $400, status "Draft."

### Step 5 — Submit and Approve the Change Order

1. Hover → Edit → change Status to **Submitted** → Save.
2. Then hover → Edit → change Status to **Approved** → Save.

**✅ Result:** Change order shows "Approved." The project's effective contract value is now $45,400.

---

## Part C — Log Project Expenses

Track the actual costs being incurred against the budget.

### Step 1 — Go to Expenses Tab

1. Click the **Expenses** tab.

### Step 2 — Log the Self-Leveling Compound Purchase

1. Click **+ New Expense**.

| Field | Value |
|---|---|
| Project | Master Bath Remodel – Johnson |
| Category | Materials |
| Description * | Self-leveling compound — 2 bags Ardex K-15 (NW corner floor leveling per CO-001) |
| Amount ($) | 89.50 |
| Date | (today) |
| Vendor | Floor & Décor — Austin |

2. Click **Create Expense**.

### Step 3 — Log a Second Expense (Tile Adhesive)

1. Click **+ New Expense** again.

| Field | Value |
|---|---|
| Project | Master Bath Remodel – Johnson |
| Category | Materials |
| Description * | Floor tile adhesive — 4 bags Mapei Kerabond T |
| Amount ($) | 124.00 |
| Date | (today) |
| Vendor | Tile Shop — Austin |

2. Click **Create Expense**.

**✅ Result:** Two expenses appear in the expenses table. **Total Expenses** KPI card increases.

---

## Part D — Review the Budget Tab

### Step 1 — Go to Budgets Tab

1. Click the **Budgets** tab.

**✅ You should see:** A table with columns: Project, Cost Code, Description, Budgeted, Actual, Variance, Var %.

This table compares what you estimated vs. what you've actually spent. A negative variance (green) means you're under budget; positive (red) means over.

### Step 2 — Verify Budget Data

Look for the Master Bath Remodel project. The actual column should reflect the expenses entered above. The variance shows how the project is tracking against the estimate.

---

## Verification Checklist

- [ ] One invoice exists with status "Sent" for the project
- [ ] **Total Invoiced** KPI card shows the invoiced amount
- [ ] **Outstanding** KPI card shows the unpaid balance
- [ ] One change order exists with status "Approved" for $400
- [ ] Two expenses exist under the project
- [ ] **Total Expenses** KPI card reflects the logged amounts
- [ ] Budget tab shows the project's cost variance

---

## Common Issues

| Problem | What to do |
|---|---|
| Invoice total shows $0 | Line items need to be added through the edit view |
| KPI cards don't update after adding invoice | Wait a moment and refresh — data fetches live |
| Change order amount doesn't affect project total | Change orders track the approved additions; the original estimated value in the project record won't auto-update — update it manually if needed |
| Budget tab is empty | Budget line items may need to be created manually or synced from the estimate |

---

## What Comes Next

The financial records are in order. The project work is nearly done — time for final inspection and project closeout.

→ Continue to: **12-project-completion.md**
