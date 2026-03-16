import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test.describe('Projects page', () => {
  test('loads projects page with KPI cards', async ({ page }) => {
    await page.goto('/projects');

    // KpiCard renders role="button" when onClick is provided.
    // Labels are rendered uppercase via CSS class but the DOM text is mixed-case,
    // so use case-insensitive regex for robustness.
    // KpiCard accessible name includes label + value text, so use filter({ hasText })
    await expect(page.locator('[role="button"]').filter({ hasText: /total projects/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /^active/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /pipeline value/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /health.*red/i }).first()).toBeVisible();
  });

  test('KPI card Active filters to production projects', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Click the "Active" KPI card — its onClick sets statusFilter to 'production'
    await page.locator('[role="button"]').filter({ hasText: /^active/i }).first().click();

    // The status filter <select> has title="Status filter"
    const statusSelect = page.getByTitle('Status filter');
    await expect(statusSelect).toBeVisible();

    // The select value should now be "in_progress" (set by the KPI card onClick)
    await expect(statusSelect).toHaveValue('in_progress');
  });

  test('KPI card Health Red filters projects', async ({ page }) => {
    await page.goto('/projects');

    // Click the "Health: Red" KPI card — its onClick sets healthFilter to 'red'
    await page.locator('[role="button"]').filter({ hasText: /health.*red/i }).first().click();

    // The health filter <select> has title="Health filter"
    const healthSelect = page.getByTitle('Health filter');
    await expect(healthSelect).toBeVisible();

    // The select value should now be "red"
    await expect(healthSelect).toHaveValue('red');
  });

  test('can open create project modal', async ({ page }) => {
    await page.goto('/projects');

    // Click the "+ New Project" button
    await page.getByRole('button', { name: /\+ new project/i }).click();

    // The ProjectModal renders a heading "New Project"
    await expect(page.getByRole('heading', { name: /new project/i })).toBeVisible();

    // Field uses label without htmlFor; match by placeholder
    await expect(page.getByPlaceholder(/johnson kitchen/i)).toBeVisible();
  });

  test('subnav shows Scheduling and Documents links', async ({ page }) => {
    await page.goto('/projects');

    // SubNav renders NavLink components which produce <a> elements
    await expect(page.getByRole('link', { name: 'Scheduling' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Documents' })).toBeVisible();
  });

  test('can filter by status', async ({ page }) => {
    await page.goto('/projects');

    const statusSelect = page.getByTitle('Status filter');
    await expect(statusSelect).toBeVisible();

    // Change to a non-empty status value
    await statusSelect.selectOption('prospect');
    await expect(statusSelect).toHaveValue('prospect');

    // After filtering, the page should show either a project grid or an empty state —
    // no error banner should be visible.
    await expect(
      page.locator('.rounded-lg.border.border-red-200'),
    ).not.toBeVisible();

    // The page should settle into one of: project cards, or the empty-state message.
    const projectsOrEmpty = page.locator(
      '.grid.gap-4, p:has-text("No projects found")',
    );
    await expect(projectsOrEmpty.first()).toBeVisible();
  });
});
