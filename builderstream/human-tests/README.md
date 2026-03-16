# BuilderStream Human Test Guide

**Version:** 3.2.0
**Last Updated:** 2026-03-16
**Platform URL:** https://buildersstream.online
**Test Login:** admin@builderstream.com / demo1234!

---

## Purpose

Step-by-step manual test scenarios for the full BuilderStream workflow — from first client contact through final payment and post-project warranty. Written for non-technical testers. No code required.

## Test Persona

Use this data consistently across all phases so records link together correctly:

> **Client:** Johnson Renovations | **Contact:** Mike Johnson
> **Email:** mike.johnson@testclient.com | **Phone:** (555) 210-4400
> **Project:** Master Bath Remodel — 1204 Oak Street, Austin TX
> **Value:** $45,000 | **Timeline:** 6 weeks

## Document Index

| # | File | Phase | Time | Module |
|---|---|---|---|---|
| 0 | `00-overview.md` | — | Read first | Navigation, personas, workflow map |
| 1 | `01-contact-creation.md` | 1–2 | 5 min | CRM → Contacts |
| 2 | `02-lead-creation.md` | 3 | 5 min | CRM → Leads |
| 3 | `03-lead-nurturing.md` | 4 | 10 min | CRM → Pipeline stages |
| 4 | `04-estimating.md` | 5–6 | 15 min | Estimating → Estimates & Proposals |
| 5 | `05-lead-to-project.md` | 7 | 5 min | CRM → Projects conversion |
| 6 | `06-project-setup.md` | 8 | 10 min | Projects → Status, Kanban |
| 7 | `07-scheduling.md` | 9 | 15 min | Scheduling → Tasks, Gantt, Crews |
| 8 | `08-field-ops.md` | 10 | 10 min | Field Ops → Clock, Logs, Expenses |
| 9 | `09-quality-safety.md` | 11 | 10 min | Quality & Safety → Inspections, Incidents |
| 10 | `10-documents.md` | 12 | 10 min | Documents → RFIs, Submittals, Photos |
| 11 | `11-financials.md` | 13 | 15 min | Financials → Invoices, Change Orders |
| 12 | `12-project-completion.md` | 14 | 10 min | Projects → Closeout, Final inspection |
| 13 | `13-client-payment.md` | 15 | 10 min | Financials → Payment portal |
| 14 | `14-post-project.md` | 16 | 15 min | Service → Warranty; Payroll → Pay run |

**Total estimated time for full run-through:** ~2.5 hours

## Running a Full End-to-End Test

1. Start at `00-overview.md` to understand navigation
2. Work through documents 01 → 14 in order
3. Each document begins with a "Prerequisite" — confirm that prior step is done before proceeding
4. Each document ends with a "Verification Checklist" — check every box before moving on
5. If a step fails, the "Common Issues" section at the bottom of each doc has solutions

## Running a Spot Test (Single Module)

Each document is self-contained. If you only need to test one area, go directly to that document. Each lists its prerequisite so you know what must exist first.

| Want to test... | Go to |
|---|---|
| Sales pipeline | `02-lead-creation.md` + `03-lead-nurturing.md` |
| Estimating and proposals | `04-estimating.md` |
| Field work tracking | `08-field-ops.md` |
| Invoice and payment flow | `11-financials.md` + `13-client-payment.md` |
| Warranty and service | `14-post-project.md` (Part A & B) |
| Payroll | `14-post-project.md` (Part C) |
