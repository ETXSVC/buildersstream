import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test('Company page loads with KPI cards', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await expect(page.getByRole('heading', { name: 'Company' })).toBeVisible();
  await expect(page.getByText('Total Employees')).toBeVisible();
  await expect(page.getByText('Total Contractors')).toBeVisible();
  await expect(page.getByText('Total Workforce')).toBeVisible();
  await expect(page.getByText('Team Members').first()).toBeVisible();
});

test('Company page shows Employees tab by default', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // Employees tab is active by default
  await expect(page.getByRole('button', { name: /Employees/i }).first()).toBeVisible();

  // Add Employee button is present
  await expect(page.getByRole('button', { name: 'Add Employee' })).toBeVisible();
});

test('Company page can switch to Contractors tab', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // Use the tab button specifically (not the KPI card div[role=button])
  await page.locator('button').filter({ hasText: /^Contractors \(/ }).click();

  // Button label changes to Add Contractor
  await expect(page.getByRole('button', { name: 'Add Contractor' })).toBeVisible();
});

test('Company page can switch to Team Members tab', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // Use the tab button specifically (not the KPI card div[role=button])
  await page.locator('button').filter({ hasText: /^Team Members \(/ }).click();

  // Add Employee button appears (Team Members tab shows all employees+contractors)
  await expect(page.getByRole('button', { name: 'Add Employee' })).toBeVisible();
});

test('Team Members tab shows employee list', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await page.locator('button').filter({ hasText: /^Team Members \(/ }).click();

  // EmployeeTable headers should be visible
  await expect(page.getByText('Name', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Trade', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Status', { exact: true }).first()).toBeVisible();
});

test('Team Members tab Add Employee modal opens and closes', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await page.locator('button').filter({ hasText: /^Team Members \(/ }).click();
  await page.getByRole('button', { name: 'Add Employee' }).click();

  await expect(page.getByRole('heading', { name: /Add Employee/ })).toBeVisible();

  // Cancel closes the modal
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByRole('heading', { name: /Add Employee/ })).not.toBeVisible();
});

test('Team Members KPI card navigates to team members tab', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // Click the "Team Members" KPI card
  await page.locator('[role="button"]').filter({ hasText: /Team Members/i }).first().click();

  // Add Employee button should now be visible (tab is active)
  await expect(page.getByRole('button', { name: 'Add Employee' })).toBeVisible();
});
