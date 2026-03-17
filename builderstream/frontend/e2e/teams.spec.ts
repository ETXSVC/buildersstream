import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test('Company page shows Teams KPI card', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await expect(page.locator('[role="button"]').filter({ hasText: /^Teams/ }).first()).toBeVisible();
});

test('Teams tab is visible on Company page', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // The tab button shows "Teams (N)"
  await expect(page.getByRole('button', { name: /Teams \(/ })).toBeVisible();
});

test('can switch to Teams tab', async ({ page }) => {
  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: /Teams \(/ }).click();

  // "New Team" button should appear
  await expect(page.getByText('New Team')).toBeVisible();
});

test('can create a team', async ({ page }) => {
  const teamName = `E2E Team ${Date.now()}`;

  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: /Teams \(/ }).click();
  await page.getByText('New Team').click();

  await page.getByPlaceholder('Team name (e.g. Framing Crew)').fill(teamName);
  await page.getByRole('button', { name: 'Create' }).click();

  // Team should appear in the list
  await expect(page.getByText(teamName)).toBeVisible({ timeout: 8000 });
});

test('can expand a team to see members', async ({ page }) => {
  const teamName = `E2E Expand ${Date.now()}`;

  await page.goto('/company');
  await page.waitForLoadState('networkidle');

  // Create a team first
  await page.getByRole('button', { name: /Teams \(/ }).click();
  await page.getByText('New Team').click();
  await page.getByPlaceholder('Team name (e.g. Framing Crew)').fill(teamName);
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByText(teamName)).toBeVisible({ timeout: 8000 });

  // Click to expand
  await page.getByText(teamName).click();

  // "Add member" link should appear
  await expect(page.getByText('Add member')).toBeVisible({ timeout: 5000 });
});

test('Team selector appears in new project modal', async ({ page }) => {
  await page.goto('/projects');
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: '+ New Project' }).click();

  // "Assigned Team" label should be in the form
  await expect(page.getByText('Assigned Team')).toBeVisible();
});

test('sidebar shows Team Messaging not Team', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();
  await expect(sidebar.getByText('Team Messaging')).toBeVisible();
  await expect(sidebar.getByText('Team', { exact: true })).not.toBeVisible();
});
