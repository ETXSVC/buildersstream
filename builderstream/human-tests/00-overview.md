# BuilderStream — Human Test Guide: Overview

**Site:** https://buildersstream.online
**Login:** admin@builderstream.com / demo1234!

---

## What Is This Guide?

This is a hands-on testing guide for the full BuilderStream workflow — from the moment a prospective client makes contact all the way through final project completion and payment collection.

Each numbered document covers one phase of the workflow. You don't need to be technical to follow them. If a step says "click the blue + New Lead button," that's exactly what you do.

---

## The Complete Workflow at a Glance

```
PHASE 1 → New contact walks in / calls / emails
             ↓
PHASE 2 → Create a Contact record (CRM)
             ↓
PHASE 3 → Open a Lead — add to the sales pipeline
             ↓
PHASE 4 → Nurture the lead (follow-ups, interactions, stage movement)
             ↓
PHASE 5 → Build an Estimate with line items
             ↓
PHASE 6 → Generate & Send a Proposal to the client
             ↓
PHASE 7 → Convert the lead → Project (upon verbal go-ahead)
             ↓
PHASE 8 → Project Setup — assign team, set dates, upload documents
             ↓
PHASE 9 → Scheduling — create tasks, build Gantt, assign crews
             ↓
PHASE 10 → Field Operations — clock in/out, daily logs, field expenses
             ↓
PHASE 11 → Quality & Safety — inspections, deficiencies, incidents
             ↓
PHASE 12 → Documents — RFIs, submittals, photo log
             ↓
PHASE 13 → Financials — invoices, change orders, expense tracking
             ↓
PHASE 14 → Project Completion — punch list, final inspection, closeout
             ↓
PHASE 15 → Final Invoice & Client Payment via portal
             ↓
PHASE 16 → Post-Project — warranties, service requests, payroll
```

---

## Navigation Reference

After logging in you will see a dark sidebar on the left with these 8 links:

| Sidebar Link | What It Opens |
|---|---|
| **Overview** | Main dashboard with metrics across all projects |
| **Projects** | Project list, Kanban board, status filters |
| **Sales** | CRM — leads, contacts, pipeline |
| **Operations** | Field Ops — time tracking, daily logs, expenses |
| **Finance & HR** | Financials, invoices, payroll |
| **Company** | Employee and contractor roster |
| **Team Messaging** | Chat channels, direct messages, archive/restore |
| **Settings** | Branding, custom fields, dunning rules |

Each section also has a **sub-navigation bar** at the top with related areas. For example, clicking **Sales** in the sidebar shows you the CRM sub-nav which includes links for **CRM** and **Estimating**.

---

## Test Documents in This Folder

| File | Phase | What You're Testing |
|---|---|---|
| `01-contact-creation.md` | 1–2 | Creating a new contact from scratch |
| `02-lead-creation.md` | 3 | Opening a lead and placing it in the pipeline |
| `03-lead-nurturing.md` | 4 | Moving the lead through stages, logging interactions |
| `04-estimating.md` | 5–6 | Building an estimate and generating a proposal |
| `05-lead-to-project.md` | 7 | Converting the approved lead into a project |
| `06-project-setup.md` | 8 | Project configuration, team, milestones |
| `07-scheduling.md` | 9 | Creating tasks, Gantt chart, crew assignment |
| `08-field-ops.md` | 10 | Clock in/out, daily logs, field expenses |
| `09-quality-safety.md` | 11 | Inspections, deficiencies, safety incidents |
| `10-documents.md` | 12 | RFIs, submittals, photo upload |
| `11-financials.md` | 13 | Invoices, change orders, expense tracking |
| `12-project-completion.md` | 14 | Final inspection, punch list, project closeout |
| `13-client-payment.md` | 15 | Sending final invoice, client pays via portal |
| `14-post-project.md` | 16 | Warranties, service requests, payroll run |

---

## Before You Start

1. Open https://buildersstream.online in Chrome or Firefox.
2. Log in with `admin@builderstream.com` / `demo1234!`
3. You should land on the **Overview** dashboard.
4. Use the test persona below when creating records — using consistent names makes it easy to find your test data later.

### Test Persona to Use Throughout

> **Client:** Johnson Renovations
> **Contact Name:** Mike Johnson
> **Email:** mike.johnson@testclient.com
> **Phone:** (555) 210-4400
> **Project:** Master Bath Remodel — 1204 Oak Street, Austin TX
> **Estimated Value:** $45,000
> **Timeline:** 6 weeks

---

## Tips

- **Green button = primary action.** Usually the thing you want to do next.
- **Amber/yellow highlights** are interactive — hover to see what they do.
- **Clicking a KPI card** (the metric boxes at the top of each page) takes you straight to the filtered list that makes up that number.
- If a modal (popup form) appears and you want to cancel, click the **Cancel** button or press **Escape**.
- If something looks wrong, refresh the page. Most data is fetched live.
