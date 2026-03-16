# Phase 7: Converting Lead to Project

**Time required:** ~5 minutes
**Where you start:** Sales → CRM → leads tab
**Prerequisite:** Mike Johnson lead in pipeline, estimate sent as proposal
**Goal:** Convert the qualified lead into an active project that can be managed through to completion.

---

## Why This Step Matters

A lead is a sales opportunity. A project is an operational commitment. The conversion step bridges these two — it creates a new project record pre-populated with the lead's data (client, value, type) and marks the lead as **Won**. After this, all work tracking, scheduling, and billing happens on the project.

---

## Step-by-Step Instructions

### Step 1 — Find the Lead

1. Go to **Sales** → **CRM**.
2. Click the **leads** tab.
3. Find Mike Johnson's lead in the table.

---

### Step 2 — Update Lead Stage to "Won" (Before Converting)

Before converting, update the stage to reflect that the client said yes:

1. Hover over the Mike Johnson lead → click **Edit**.
2. Change **Pipeline Stage** to the stage closest to "Won" or "Contract Signed" in your pipeline.
3. Click **Save Changes**.

**✅ Result:** Stage now shows Won/Proposal Sent (the final stage before conversion).

---

### Step 3 — Convert the Lead to a Project

1. Hover over the Mike Johnson lead row.
2. Look for a **Convert** action (may appear as "Convert to Project" or a similar button on hover).
3. Click it.

> If no Convert button is visible, go to **Projects** instead and create the project manually using the data from the lead — then mark the lead as Won.

**✅ If conversion works automatically:** A new project is created and the lead status changes to "Won." You'll be navigated to (or can manually go to) the Projects section to find it.

---

### Step 4 — Alternative: Create Project Manually

If the lead doesn't have a direct "Convert" button, create the project manually:

1. In the left sidebar, click **Projects**.
2. Click **+ New Project**.
3. Fill in the form using the lead data:

| Field | Value |
|---|---|
| Project Name * | Master Bath Remodel – Johnson |
| Project Type | Kitchen & Bath |
| Client | Mike Johnson |
| Address | 1204 Oak Street |
| City | Austin |
| State | TX |
| Estimated Value ($) | 45000 |
| Start Date | (two weeks from today) |
| Target Completion | (eight weeks from today) |
| Description | Master bathroom remodel. Walk-in shower, new tile, double vanity, plumbing and electrical. Referred project from neighbor. |

4. Click **Create Project**.

---

### Step 5 — Mark the Lead as Won (if not auto-updated)

1. Go back to **Sales** → **CRM** → leads tab.
2. Hover over Mike Johnson's lead → click **Edit**.
3. Change stage to the "Won" stage.
4. Click **Save Changes**.

**✅ Result:** The lead is marked Won and the project exists in Projects.

---

## Verification Checklist

- [ ] A new project "Master Bath Remodel – Johnson" exists in the Projects list
- [ ] Project shows client as Mike Johnson
- [ ] Estimated value shows $45,000
- [ ] Project status shows **Prospect** (the starting status)
- [ ] The lead in CRM now shows a Won stage
- [ ] **Pipeline Value** in CRM may decrease (lead is closed)

---

## Understanding Project Status

Projects start at **Prospect** and move through statuses as work progresses:

```
Prospect → Site Survey → Proposal → Acceptance → In Progress →
Milestones → Finish Project → Billing → Paid / Complete
(Canceled is available from any status)
```

You'll manually advance the status in the project record as milestones are hit.

---

## Common Issues

| Problem | What to do |
|---|---|
| Project doesn't appear in list | Use the search bar or clear any status/health filters |
| Client field was blank in conversion | Edit the project and assign Mike Johnson as client |
| Two projects created by accident | Delete the duplicate using the delete action on hover |

---

## What Comes Next

The project record exists. Now configure it properly: assign the project manager, set key dates, and link the estimate.

→ Continue to: **06-project-setup.md**
