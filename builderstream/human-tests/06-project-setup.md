# Phase 8: Project Setup

**Time required:** ~10 minutes
**Where you start:** Projects section
**Prerequisite:** "Master Bath Remodel – Johnson" project exists (see `05-lead-to-project.md`)
**Goal:** Fully configure the project — advance status, set dates, verify all key info is in place.

---

## Why This Step Matters

A project record is more than a name and a value. Before work can begin, the system needs to know who's managing it, when it starts and ends, and that a contract is in place. The status machine enforces these requirements — you can't move a project to "In Progress" without a start date and team assignment.

---

## Notes for v3.3.0

Projects can now have an **Assigned Team** selected in the create/edit modal. The team name appears on the project card. Teams are created and managed under **Company → Teams** tab.

---

## Part A — Find and Review the Project

### Step 1 — Go to Projects

1. In the left sidebar, click **Projects**.

**✅ You should see:** The project list with KPI cards at the top (Total Projects, Active, Pipeline Value, Health: Red). Your new project should be in the list.

### Step 2 — Verify the Project

Confirm these details are correct on the card/row:

- Name: Master Bath Remodel – Johnson
- Status: Prospect
- Client: Mike Johnson
- Estimated Value: $45,000
- Health score indicator is present

---

## Part B — Advance Status to "Acceptance"

This status means: client has accepted the proposal and signed or verbally committed.

### Step 1 — Edit the Project

1. Hover over the project row → click **Edit** (pencil icon).
2. The "Edit Project" modal opens.

### Step 2 — Update Fields

| Field | Value |
|---|---|
| Project Name | Master Bath Remodel – Johnson (unchanged) |
| Start Date | (two weeks from today — actual mobilization date) |
| Target Completion | (eight weeks from Start Date) |

3. Click **Save Changes**.

### Step 3 — Advance the Status

To move the project through statuses, look for a **Status** dropdown on the project detail or the edit modal. Move it forward one step at a time:

1. Edit the project → change Status to **Site Survey** → Save.
2. Edit again → change Status to **Proposal** → Save.
3. Edit again → change Status to **Acceptance** → Save.

> *(In a real workflow you'd do this one step at a time over days/weeks as each milestone is actually reached. For testing, moving through them quickly is fine.)*

**✅ Result:** Project status shows "Acceptance."

---

## Part C — Advance to "In Progress"

The "In Progress" status requires a start date and team to be assigned. (If the system blocks you, add those items first.)

### Step 1 — Edit the Project

1. Edit → change Status to **In Progress** → Save.

> If the system gives you a validation error like "Start date required" or "Team required," add those values first then try again.

**✅ Result:** Status shows "In Progress." The project now appears when you click the **Active** KPI card.

---

## Part D — Try the Kanban View

1. On the Projects page, click the **Kanban View** button (near the top right).
2. You should see columns for each status with project cards.
3. Find "Master Bath Remodel – Johnson" in the "In Progress" column.
4. Click **Kanban View** again (or the List button) to switch back to list view.

**✅ Result:** Project visible in both list and kanban views.

---

## Part E — Test the KPI Card Navigation

From the Projects page:

1. Click the **Active** KPI card → the list should filter to show only In Progress projects. Your project should be visible.
2. Click the **Total Projects** KPI card → filter clears, all projects show.
3. Click **Health: Red** → shows only projects with critical health score (may be empty if the project is new).

---

## Verification Checklist

- [ ] Project status is "In Progress"
- [ ] Start Date and Target Completion are set
- [ ] Clicking **Active** KPI card shows this project in the filtered list
- [ ] Project has a health score visible (number and color)
- [ ] Project appears correctly in Kanban view

---

## Project Health Score Explained

BuilderStream auto-calculates a 0–100 health score for active projects:

| Component | Weight | Green | Yellow | Red |
|---|---|---|---|---|
| Budget variance | 40% | Under budget | <10% over | >10% over |
| Schedule variance | 30% | On time | <1 wk late | >1 wk late |
| Overdue items | 30% | None | 1–2 items | 3+ items |

A new project starts green. As time passes and data is entered, the score updates automatically every hour.

---

## Common Issues

| Problem | What to do |
|---|---|
| Can't advance to In Progress | Check that Start Date is set and at least one team member is assigned |
| Health shows "red" immediately | Start Date may be in the past — update it |
| Project not visible in Kanban | Check that status is not "Prospect" — Kanban shows active statuses |

---

## What Comes Next

The project is configured and active. Now build the schedule — tasks, Gantt chart, and crew assignments.

→ Continue to: **07-scheduling.md**
