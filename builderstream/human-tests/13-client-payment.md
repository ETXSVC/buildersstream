# Phase 15: Final Invoice & Client Payment Portal

**Time required:** ~10 minutes
**Where you start:** Finance & HR → Financials → Invoices
**Prerequisite:** Project is in "Billing" status, Draw #1 invoice was previously sent
**Goal:** Create the final invoice, send a payment link to the client, and record the payment.

---

## Why This Step Matters

The client payment portal is how BuilderStream gets you paid faster. Instead of mailing a PDF invoice and waiting for a check, you send the client a secure link. They can view the invoice and pay by credit card or ACH directly. You get notified immediately and the invoice is automatically marked Paid.

---

## Part A — Create the Final Invoice

### Scenario

Draw #1 covered 35% ($15,750). The project is complete. Total contract = $45,400 (including CO-001). Draw #1 paid = $15,750. Balance remaining = **$29,650**.

### Step 1 — Navigate to Financials

1. Left sidebar → **Finance & HR** → **Financials** tab (if not default) → **Invoices** tab.

### Step 2 — Create Final Invoice

1. Click **+ New Invoice**.

| Field | Value |
|---|---|
| Project * | Master Bath Remodel – Johnson |
| Status | Draft |
| Due Date | (today + 10 days) |

2. Click **Create Invoice**.

### Step 3 — Add Line Items and Update Total

1. Hover → Edit the new invoice.
2. Add line items:

| Description | Amount |
|---|---|
| Remaining balance — Master Bath Remodel (65% completion draw) | $27,050.00 |
| Change Order CO-001: Floor self-leveling compound | $400.00 |
| Retainage release (per contract) | $2,200.00 |
| **Total** | **$29,650.00** |

3. Change Status to **Draft** (keep as draft until ready to send).
4. Save.

### Step 4 — Review the Invoice

Before sending, confirm:
- Project is correct
- Amount is $29,650
- Due date is set
- Client name will appear on the invoice

---

## Part B — Send the Invoice via Payment Portal

### Step 1 — Change Status to Sent

1. Hover → Edit the invoice.
2. Change Status to **Sent**.
3. Save.

**✅ Result:** Status shows "Sent." The **Outstanding** KPI card increases by $29,650.

### Step 2 — Find the Payment Portal Link

BuilderStream generates a secure, tokenized payment link for each invoice. Look for:

- A **"Send to Client"** or **"Copy Payment Link"** button on the invoice row
- Or look in the invoice edit modal for a payment URL field

The link looks like: `https://buildersstream.online/pay/[unique-token]`

### Step 3 — Test the Client Portal

1. Copy the payment link.
2. Open it in a **new private/incognito browser window** (so you're not logged in as admin).

**✅ You should see:** A clean invoice page showing:
- Company logo and name (BuilderStream or your org's branding)
- Invoice number
- Project name: Master Bath Remodel – Johnson
- Client name: Mike Johnson / Johnson Renovations
- Line items with amounts
- **Total Due: $29,650.00**
- A **"Pay Now"** button (powered by Stripe)

> **Note:** In the test environment with a dummy Stripe key, clicking "Pay Now" will open Stripe's test payment form. Use Stripe test card **4242 4242 4242 4242**, any future expiry, any CVC.

### Step 4 — Simulate a Payment (Test Card)

If the Stripe integration is active in test mode:

1. On the payment portal page, click **Pay Now**.
2. Enter Stripe test card: `4242 4242 4242 4242`
3. Expiry: `12/29` (any future date)
4. CVC: `424`
5. Name: `Mike Johnson`
6. Click **Pay**.

**✅ Expected result:** Payment processes successfully. You'll see a "Payment confirmed" screen on the portal.

Back in the admin app, the invoice status should automatically update to **Paid** (this happens via a Stripe webhook).

---

## Part C — Mark Invoice Paid Manually (If Stripe Not Configured)

If Stripe test payments aren't working:

1. Go back to Financials → Invoices tab.
2. Hover over the final invoice row → Edit.
3. Change Status to **Paid**.
4. Save.

**✅ Result:** Invoice shows "Paid." **Outstanding** KPI card decreases. **Total Invoiced** is accurate.

---

## Part D — Confirm All Invoices Are Paid

Review Draw #1 as well:

1. Find the Draw #1 invoice (INV-2026-001 from Phase 13).
2. If it's still showing "Sent" status, mark it as **Paid** (or simulate payment through the portal if a link is available).

**✅ Final financials check:**
- Total Invoiced: ~$45,400
- Outstanding: $0
- Overdue: $0

---

## Verification Checklist

- [ ] Final invoice exists with total $29,650
- [ ] Invoice status is "Paid" (via portal or manual update)
- [ ] **Outstanding** KPI card shows $0
- [ ] **Overdue** KPI card shows $0
- [ ] Client payment portal page loads correctly from the payment link
- [ ] Portal shows invoice details without requiring login

---

## Common Issues

| Problem | What to do |
|---|---|
| Payment portal link not visible | Look for a "Copy Link" or share button on the invoice row; if missing, the feature may use a direct URL format like `/pay/[invoice-id]` |
| Stripe checkout doesn't load | The Stripe key in the environment may be a placeholder — mark the invoice Paid manually |
| Invoice stays "Sent" after portal payment | Stripe webhook may not be configured — mark Paid manually after testing the portal UI |
| Payment portal shows "Invalid or expired link" | The invoice token may have expired or the link was constructed incorrectly |

---

## What Comes Next

The project is paid and complete. Now handle the post-project items: register the workmanship warranty, add any service requests that come in during the warranty period, and run the payroll for the project.

→ Continue to: **14-post-project.md**
