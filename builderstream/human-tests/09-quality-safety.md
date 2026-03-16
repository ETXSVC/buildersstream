# Phase 11: Quality & Safety

**Time required:** ~10 minutes
**Where you start:** Operations → Quality & Safety (sub-nav)
**Prerequisite:** Project is In Progress
**Goal:** Schedule a rough plumbing inspection, log a deficiency, and record a safety observation.

---

## Why This Step Matters

Quality inspections create a formal record that work was checked and met standards — essential for protecting against warranty claims. Safety incident logging is a legal requirement and helps identify patterns before someone gets hurt. Both feed into project health scoring.

---

## Navigation

1. In the left sidebar, click **Operations**.
2. In the sub-navigation bar at the top, click **Quality & Safety**.

**✅ You should see:** Four tabs: **Inspections**, **Deficiencies**, **Incidents**, **Safety Incidents** and four KPI cards: Inspections, Pass Rate, Open Deficiencies, Safety Incidents.

---

## Part A — Schedule and Run an Inspection

### Step 1 — Go to Inspections Tab

The default tab when you arrive is usually **Inspections**.

### Step 2 — Create a New Inspection

1. Click **+ New Inspection**.

**✅ You should see:** A modal titled **"New Inspection"**.

### Step 3 — Fill In Inspection Details

| Field | Value |
|---|---|
| Type | Plumbing |
| Status | Scheduled |
| Project | Master Bath Remodel – Johnson |
| Scheduled Date | (today's date) |
| Score | (leave blank — filled in after inspection) |
| Notes | Rough plumbing inspection for master bath remodel. Verify all drain lines, supply rough-in, and shower drain location prior to tile. |

### Step 4 — Save

1. Click **Create Inspection**.

**✅ Result:** Inspection appears in the table with status "Scheduled" and an auto-generated inspection number (e.g., INS-2026-001).

---

### Step 5 — Mark the Inspection as Passed

After the inspector has reviewed the work:

1. Hover over the inspection row → click **Edit**.
2. Update:

| Field | Value |
|---|---|
| Status | Passed |
| Score | 92 |
| Notes | All rough plumbing passed inspection. Minor note: add sleeve at penetration point through bottom plate. |

3. Click **Save Changes**.

**✅ Result:** Inspection status shows "Passed" with a score of 92. The **Pass Rate** KPI card updates.

---

## Part B — Log a Deficiency

A deficiency is a quality issue found during inspection that needs to be corrected.

### Step 1 — Go to Deficiencies Tab

1. Click the **Deficiencies** tab.

**✅ You should see:** A table with columns: Description, Project, Inspection, Severity, Assigned To, Due Date, Status.

> **Note:** Deficiencies are typically created automatically when an inspection finds issues. If your UI doesn't auto-create them, they may be managed through the inspection detail view. For this test, note whether deficiencies exist from the inspection above or if you need to add them manually.

---

## Part C — Record a Safety Incident (Near Miss)

Even if no one was hurt, near-miss events must be logged.

### Step 1 — Go to Safety Incidents Tab

1. Click the tab labeled **Safety Incidents** (or **Incidents** depending on your screen).

**✅ You should see:** A table with columns: Incident #, Project, Type, Severity, Reported By, Date, Injuries, Status.

### Step 2 — Create a New Incident

1. Click **+ New Incident**.

**✅ You should see:** A modal titled **"New Safety Incident"**.

### Step 3 — Fill In Incident Details

| Field | Value |
|---|---|
| Incident Type | Near Miss |
| Severity | Near Miss |
| Project | Master Bath Remodel – Johnson |
| Incident Date * | (today's date) |
| Description * | Worker slipped on wet concrete floor during demolition cleanup. No injury occurred. Slip hazard identified near shower drain area. Corrective action: place non-slip mat and wet floor sign during all wet work. |
| Injuries Count | 0 |
| OSHA Recordable | No |

### Step 4 — Save

1. Click **Create Incident** (or equivalent button).

**✅ Result:** Incident appears in the table with an auto-generated incident number, severity "Near Miss," and 0 injuries. The **Safety Incidents** KPI card count increases.

---

## Part D — Create a Second Inspection (Final)

Schedule the final inspection for the end of the project (you'll complete it later):

1. Click **+ New Inspection**.

| Field | Value |
|---|---|
| Type | Final |
| Status | Scheduled |
| Project | Master Bath Remodel – Johnson |
| Scheduled Date | (project completion date — 6 weeks from now) |
| Notes | Final walkthrough inspection before client handover. Check all tile grouting, fixture operation, paint finish, and caulking. |

2. Click **Create Inspection**.

**✅ Result:** A second inspection exists with type "Final" and status "Scheduled."

---

## Verification Checklist

- [ ] At least one inspection exists with status "Passed" and score 92
- [ ] **Pass Rate** KPI card shows > 0%
- [ ] **Inspections** KPI card shows at least 2
- [ ] One near-miss safety incident exists with 0 injuries
- [ ] **Safety Incidents** KPI card shows at least 1
- [ ] **Open Deficiencies** KPI card shows the count from the inspection

---

## Common Issues

| Problem | What to do |
|---|---|
| Score field is missing | Score field only appears when status is Passed or Failed |
| Safety Incidents tab not visible | It may be labeled "Incidents" — check all four tabs |
| Deficiency count doesn't update | Deficiencies may need to be created through the inspection detail — check the inspection row for a "View" or detail option |
| OSHA Recordable toggle not responding | This is a Yes/No toggle — click once to flip |

---

## What Comes Next

Inspections passed and safety is documented. Now manage the paper trail — RFIs, submittals, and the photo log.

→ Continue to: **10-documents.md**
