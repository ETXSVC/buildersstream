import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test('sidebar has 8 top-level nav items', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();

  await expect(sidebar.getByText('Overview')).toBeVisible();
  await expect(sidebar.getByText('Projects')).toBeVisible();
  await expect(sidebar.getByText('Sales')).toBeVisible();
  await expect(sidebar.getByText('Operations')).toBeVisible();
  await expect(sidebar.getByText('Finance & HR')).toBeVisible();
  await expect(sidebar.getByText('Company')).toBeVisible();
  await expect(sidebar.getByText('Team')).toBeVisible();
  await expect(sidebar.getByText('Settings')).toBeVisible();
});

test('navigates to each main section', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();

  await sidebar.getByText('Projects').click();
  await expect(page).toHaveURL(/\/projects/);

  await sidebar.getByText('Sales').click();
  await expect(page).toHaveURL(/\/crm/);

  await sidebar.getByText('Operations').click();
  await expect(page).toHaveURL(/\/field-ops/);

  await sidebar.getByText('Finance & HR').click();
  await expect(page).toHaveURL(/\/financials/);
});

test('Settings opens branding page', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();
  await sidebar.getByText('Settings').click();

  await expect(page).toHaveURL(/\/settings/);
});

test('Company page loads', async ({ page }) => {
  await page.goto('/company');

  await expect(page.getByRole('heading', { name: 'Company' })).toBeVisible();

  // Expect 4 KPI cards
  const kpiCards = page.locator('[class*="kpi"], .rounded-xl, .rounded-lg').filter({ hasText: /Employees|Contractors|Workforce|Workers/i });
  // Use a broader approach: check that at least 4 cards with known labels are visible
  await expect(page.getByText('Total Employees')).toBeVisible();
  await expect(page.getByText('Total Contractors')).toBeVisible();
  await expect(page.getByText('Total Workforce')).toBeVisible();
  await expect(page.getByText('Active Workers')).toBeVisible();
});

test('Team page loads collaboration', async ({ page }) => {
  await page.goto('/collaboration');
  await page.waitForLoadState('networkidle');

  // The chat sidebar shows "Channels" section heading
  await expect(page.getByText('Channels', { exact: false })).toBeVisible({ timeout: 10000 });
});
