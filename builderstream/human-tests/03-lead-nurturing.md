# Phase 4: Lead Nurturing

**Time required:** ~10 minutes
**Where you start:** Sales → CRM → leads tab
**Prerequisite:** Mike Johnson lead exists (see `02-lead-creation.md`)
**Goal:** Move the lead through the pipeline stages and log interactions along the way.

---

## Why This Step Matters

Most leads don't convert immediately. The nurturing process — follow-up calls, site visits, answered questions — is what moves a prospect from "interested" to "signed." The CRM pipeline tracks every stage and interaction so no lead falls through the cracks.

---

## Pipeline Stages Reference

Leads move left to right through these stages (your org may have slightly different names):

```
New Lead → Contacted → Qualified → Site Visit → Proposal Sent → Negotiation → Won / Lost
```

Each stage represents how far along the relationship is. Moving a lead forward is done by editing it and changing the stage.

---

## Part A — Log a Phone Call Interaction

### Step 1 — Find the Lead

1. Go to **Sales** → **CRM** → **leads** tab.
2. Find the Mike Johnson lead in the table.

### Step 2 — Edit the Lead

1. Hover over the Mike Johnson row.
2. Click the **Edit** (pencil) icon that appears on hover, or click directly on Mike Johnson's name.

**✅ You should see:** The "Edit Lead" modal opens pre-filled with the values you entered.

### Step 3 — Update Stage and Follow-up

Change these fields:

| Field | New Value |
|---|---|
| Pipeline Stage | Contacted |
| Urgency | Hot – Immediate (he called back and wants to move quickly) |
| Next Follow-up | (set to tomorrow) |

### Step 4 — Save

1. Click **Save Changes**.

**✅ Result:** The lead now shows "Contacted" in the Stage column and "Hot" urgency.

---

## Part B — Move Lead to "Qualified"

After a qualifying conversation where you confirmed budget, timeline, and scope:

### Step 1 — Edit the Lead Again

1. Hover over the Mike Johnson row → click **Edit**.

### Step 2 — Update Stage

| Field | New Value |
|---|---|
| Pipeline Stage | Qualified |
| Next Follow-up | (one week from today — for a site visit) |

### Step 3 — Save

**✅ Result:** Stage shows "Qualified."

---

## Part C — Schedule a Site Visit

### Step 1 — Edit the Lead

1. Hover → **Edit**.

### Step 2 — Update Stage

| Field | New Value |
|---|---|
| Pipeline Stage | Site Visit |
| Estimated Start | (today + 2 weeks) |
| Next Follow-up | (today + 5 days — to confirm site visit appointment) |

### Step 3 — Save

**✅ Result:** Stage shows "Site Visit."

---

## Verification Checklist

After working through Parts A, B, and C:

- [ ] Mike Johnson lead shows stage "Site Visit"
- [ ] Urgency shows "Hot"
- [ ] **Hot Leads** KPI card count shows at least 1
- [ ] Estimated value is still $45,000
- [ ] Next follow-up date is updated

---

## Understanding Lead Score

Look at the **Score** column (or the score shown in the contact record). BuilderStream calculates a score 0–100 based on:

| Factor | Max Points | Our Lead Scores |
|---|---|---|
| Estimated value ($45k = 10pts) | 30 | 10 |
| Urgency (Hot = 20pts) | 20 | 20 |
| Source quality | 20 | 20 (referral) |
| Engagement (interactions) | 20 | variable |
| Response time | 10 | variable |

A score of 50+ is a well-qualified lead.

---

## Common Issues

| Problem | What to do |
|---|---|
| Stage dropdown doesn't have expected stages | Stages are configured in Settings → your org may use custom stages |
| Lead score doesn't update immediately | Scores recalculate hourly in the background — check back in a few minutes |
| Can't find the Edit button | Hover slowly over the row — the buttons appear on hover |

---

## What Comes Next

The lead has been through a site visit and the client is ready for a price. Time to build an estimate.

→ Continue to: **04-estimating.md**
