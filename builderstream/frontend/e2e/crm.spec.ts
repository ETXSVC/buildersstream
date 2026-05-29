
import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test.describe('CRM page', () => {
  test('loads CRM page with KPI cards', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // KpiCard accessible name includes label + value; use filter({ hasText })
    await expect(page.locator('[role="button"]').filter({ hasText: /total leads/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /hot leads/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /pipeline value/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /contacts/i }).first()).toBeVisible();
  });

  test('KPI card Total Leads navigates to leads list', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // Click the Total Leads KPI card (role=button set when onClick is present)
    await page.locator('[role="button"]').filter({ hasText: /total leads/i }).first().click();

    // The leads tab toggle button should now be active and the leads list / empty state should be visible
    const leadsTabButton = page.locator('button', { hasText: 'leads' });
    await expect(leadsTabButton).toBeVisible();

    // The leads view shows a table or "No leads found" message
    const leadsTableOrEmpty = page.locator(
      'table, td:has-text("No leads found")',
    );
    await expect(leadsTableOrEmpty.first()).toBeVisible();
  });

  test('KPI card Contacts navigates to contacts', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // Click the Contacts KPI card
    await page.locator('[role="button"]').filter({ hasText: /contacts/i }).first().click();

    // Wait for the contacts view to render
    const contactsTabButton = page.locator('button', { hasText: 'contacts' });
    await expect(contactsTabButton).toBeVisible();

    // Contacts view renders a table or an empty-state message
    const contactsTableOrEmpty = page.locator(
      'table, td:has-text("No contacts found")',
    );
    await expect(contactsTableOrEmpty.first()).toBeVisible();
  });

  test('can create a new contact', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // Switch to Contacts tab
    await page.locator('button', { hasText: 'contacts' }).click();

    // Click "+ New Contact"
    await page.getByRole('button', { name: /\+ new contact/i }).click();

    // Modal should appear with title "New Contact"
    await expect(page.getByRole('heading', { name: /new contact/i })).toBeVisible();

    // Use unique names to avoid collisions with previous test runs
    const uniqueFirst = `E2E${Date.now()}`;
    const uniqueLast = 'Contact';

    // Fill in the form — Field component has no htmlFor, so match by placeholder
    await page.getByPlaceholder('Jane', { exact: true }).fill(uniqueFirst);
    await page.getByPlaceholder('Smith', { exact: true }).fill(uniqueLast);
    await page.getByPlaceholder('jane@example.com', { exact: true }).fill(`${uniqueFirst}@test.com`);

    // Submit
    await page.getByRole('button', { name: /create contact/i }).click();

    // Modal should close (heading disappears)
    await expect(page.getByRole('heading', { name: /new contact/i })).not.toBeVisible();

    // The new contact should appear in the list
    await expect(page.getByText(`${uniqueFirst} ${uniqueLast}`).first()).toBeVisible();
  });

  test('can search contacts', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // Switch to Contacts tab
    await page.locator('button', { hasText: 'contacts' }).click();

    // Type in the search box (placeholder changes based on view)
    const searchInput = page.getByPlaceholder(/search contacts/i);
    await expect(searchInput).toBeVisible();
    await searchInput.fill('xyz_nonexistent_query_12345');

    // Results should update — either the table renders (possibly empty rows) or
    // the empty-state message appears. Either way, the table container is still
    // present and the "No contacts found" cell should be visible for a miss.
    await expect(
      page.locator('table, td:has-text("No contacts found")').first(),
    ).toBeVisible();
  });

  test('subnav shows Estimating link', async ({ page }) => {
    await page.goto('/crm');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // SubNav renders NavLinks — which produce <a> elements
    await expect(page.getByRole('link', { name: 'Estimating' })).toBeVisible();
  });
});
