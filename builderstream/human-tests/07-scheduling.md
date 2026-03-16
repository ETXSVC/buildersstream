# Phase 9: Scheduling

**Time required:** ~15 minutes
**Where you start:** Projects → Scheduling (sub-nav) or left sidebar → Projects → Scheduling tab
**Prerequisite:** Project "Master Bath Remodel – Johnson" is In Progress
**Goal:** Create a task schedule, view the Gantt chart, and assign a crew.

---

## Why This Step Matters

A schedule turns intentions into commitments. Each task has a start date, end date, and owner. The Gantt chart gives you a visual timeline of the entire project so you can spot overlaps, critical path bottlenecks, and deadline risks at a glance.

---

## Navigation

You can reach Scheduling two ways:
- **Left sidebar** → Projects → the page has a sub-nav bar → click **Scheduling**
- **Left sidebar** → Projects → click into sub-nav **Scheduling** tab

Either way you should land on the Scheduling page with four tabs: **tasks**, **gantt**, **crews**, **equipment**.

---

## Part A — Add a Crew

Before creating tasks, set up the crew you'll assign.

### Step 1 — Go to Crews Tab

1. Click the **crews** tab.

**✅ You should see:** A crews table (may be empty or have existing crews).

### Step 2 — Create a New Crew

1. Click **+ New Crew**.

**✅ You should see:** A modal titled **"New Crew"**.

### Step 3 — Fill In Crew Details

| Field | Value |
|---|---|
| Crew Name * | Johnson Remodel Team |
| Trade * | Finish Carpentry |
| Foreman | (leave blank or select yourself) |
| Crew Members | (leave blank for now) |
| Hourly Rate ($) | 85 |
| Status | Active |

### Step 4 — Save

1. Click **Create Crew**.

**✅ Result:** Crew appears in the crews table.

---

## Part B — Create the Project Schedule (Tasks)

### Step 1 — Go to Tasks Tab

1. Click the **tasks** tab.

**✅ You should see:** A tasks table with columns: Task, Project, Start, End, Progress, Crew, Status, CP (Critical Path).

### Step 2 — Create Tasks

Create each task below by clicking **+ New Task** for each one:

---

**Task 1: Demolition**

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Task Name * | Demolition |
| Type | Task |
| Status | Not Started |
| Start Date | (project start date) |
| End Date | (start + 2 days) |
| Estimated Hours | 16 |
| % Complete | 0 |
| Assigned Crew | Johnson Remodel Team |

Click **Create Task**.

---

**Task 2: Rough Plumbing**

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Task Name * | Rough Plumbing |
| Type | Task |
| Status | Not Started |
| Start Date | (Task 1 end + 1 day) |
| End Date | (start + 3 days) |
| Estimated Hours | 24 |
| % Complete | 0 |
| Assigned Crew | Johnson Remodel Team |

---

**Task 3: Rough Electrical**

| Field | Value |
|---|---|
| Task Name * | Rough Electrical |
| Type | Task |
| Start Date | (same as Rough Plumbing — can run parallel) |
| End Date | (start + 2 days) |
| Estimated Hours | 16 |

---

**Task 4: Tile Installation**

| Field | Value |
|---|---|
| Task Name * | Tile – Floor & Shower Walls |
| Type | Task |
| Start Date | (after rough plumbing and electrical are done) |
| End Date | (start + 5 days) |
| Estimated Hours | 40 |
| Assigned Crew | Johnson Remodel Team |

---

**Task 5: Vanity & Fixture Installation**

| Field | Value |
|---|---|
| Task Name * | Vanity & Fixtures Install |
| Type | Task |
| Start Date | (after tile) |
| End Date | (start + 2 days) |
| Estimated Hours | 16 |

---

**Task 6: Paint & Finishes**

| Field | Value |
|---|---|
| Task Name * | Paint & Final Finishes |
| Type | Task |
| Start Date | (after vanity install) |
| End Date | (start + 2 days) |
| Estimated Hours | 12 |

---

**Task 7: Final Inspection Milestone**

| Field | Value |
|---|---|
| Task Name * | Final Inspection |
| Type | Milestone |
| Start Date | (project target completion date) |
| End Date | (same day as start) |
| Estimated Hours | 2 |

---

### Step 3 — Verify Tasks Appear

After creating all tasks, the tasks table should show 7 rows for this project. Each row shows the task name, project name, dates, crew assignment, and status.

---

## Part C — View the Gantt Chart

### Step 1 — Switch to Gantt Tab

1. Click the **gantt** tab.

**✅ You should see:** A horizontal bar chart with tasks on the left and a timeline calendar on the right. Each task is a bar spanning its start-to-end dates.

### Step 2 — Verify the Timeline

- Demolition is the first bar (leftmost)
- Final Inspection is the last bar (rightmost)
- Parallel tasks (Rough Plumbing + Rough Electrical) overlap on the timeline
- The timeline spans roughly 6 weeks

### Step 3 — Drag to Adjust (Optional)

> Gantt bars can be dragged to shift dates. Try dragging the Tile bar one day later and confirm the date updates.

---

## Verification Checklist

- [ ] 7 tasks exist for the Master Bath Remodel project
- [ ] All tasks have start and end dates
- [ ] "Johnson Remodel Team" crew is assigned to 4 of the tasks
- [ ] Gantt chart shows all tasks in a timeline view
- [ ] KPI card **Total Tasks** count includes your new tasks
- [ ] Final Inspection task has type "Milestone"

---

## Common Issues

| Problem | What to do |
|---|---|
| Gantt shows tasks from all projects | This is expected — use the Gantt to see the full picture |
| Tasks don't appear in Gantt | They may need to be refreshed — switch to tasks tab and back |
| Crew dropdown empty in task form | Create the crew first (Part A above) |
| Milestone doesn't look different in Gantt | Milestones render as a diamond marker rather than a bar |

---

## What Comes Next

The schedule is built. Now it's time to start work — clock in, log daily progress, and track field expenses.

→ Continue to: **08-field-ops.md**
