import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test.describe('Projects page', () => {
  test('loads projects page with KPI cards', async ({ page }) => {
    await page.goto('/projects');

    await expect(page.locator('[role="button"]').filter({ hasText: /total projects/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /^active/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /pipeline value/i }).first()).toBeVisible();
    await expect(page.locator('[role="button"]').filter({ hasText: /health.*red/i }).first()).toBeVisible();
  });

  test('KPI card Total Projects clears filters', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    // Set a filter first, then click Total Projects to clear it
    await page.getByTitle('Status filter').selectOption('prospect');
    await page.locator('[role="button"]').filter({ hasText: /total projects/i }).first().click();

    await expect(page.getByTitle('Status filter')).toHaveValue('');
  });

  test('KPI card Active filters to production projects', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    await page.locator('[role="button"]').filter({ hasText: /^active/i }).first().click();

    const statusSelect = page.getByTitle('Status filter');
    await expect(statusSelect).toBeVisible();
    await expect(statusSelect).toHaveValue('in_progress');
  });

  test('KPI card Health Red filters projects', async ({ page }) => {
    await page.goto('/projects');

    await page.locator('[role="button"]').filter({ hasText: /health.*red/i }).first().click();

    const healthSelect = page.getByTitle('Health filter');
    await expect(healthSelect).toBeVisible();
    await expect(healthSelect).toHaveValue('red');
  });

  test('subnav shows Scheduling and Documents links', async ({ page }) => {
    await page.goto('/projects');

    await expect(page.getByRole('link', { name: 'Scheduling' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Documents' })).toBeVisible();
  });

  test('can filter by status', async ({ page }) => {
    await page.goto('/projects');

    const statusSelect = page.getByTitle('Status filter');
    await expect(statusSelect).toBeVisible();

    await statusSelect.selectOption('prospect');
    await expect(statusSelect).toHaveValue('prospect');

    await expect(page.locator('.rounded-lg.border.border-red-200')).not.toBeVisible();
    const projectsOrEmpty = page.locator('.grid.gap-4, p:has-text("No projects found")');
    await expect(projectsOrEmpty.first()).toBeVisible();
  });

  test('can filter by health status', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const healthSelect = page.getByTitle('Health filter');
    await healthSelect.selectOption('green');
    await expect(healthSelect).toHaveValue('green');

    await expect(page.locator('.rounded-lg.border.border-red-200')).not.toBeVisible();
  });

  test('search input is visible and accepts text', async ({ page }) => {
    await page.goto('/projects');

    const search = page.getByPlaceholder('Search projects…');
    await expect(search).toBeVisible();

    await search.fill('test');
    await expect(search).toHaveValue('test');

    await expect(page.locator('.rounded-lg.border.border-red-200')).not.toBeVisible();
  });

  test('can open create project modal', async ({ page }) => {
    await page.goto('/projects');

    await page.getByRole('button', { name: /\+ new project/i }).click();

    await expect(page.getByRole('heading', { name: /new project/i })).toBeVisible();
    await expect(page.getByPlaceholder(/johnson kitchen/i)).toBeVisible();
  });

  test('create project modal has required fields', async ({ page }) => {
    await page.goto('/projects');
    await page.getByRole('button', { name: /\+ new project/i }).click();

    await expect(page.getByRole('heading', { name: /new project/i })).toBeVisible();
    await expect(page.getByPlaceholder(/johnson kitchen/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /save|create/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /cancel/i })).toBeVisible();
  });

  test('create project modal closes on cancel', async ({ page }) => {
    await page.goto('/projects');
    await page.getByRole('button', { name: /\+ new project/i }).click();

    await expect(page.getByRole('heading', { name: /new project/i })).toBeVisible();

    await page.getByRole('button', { name: /cancel/i }).click();

    await expect(page.getByRole('heading', { name: /new project/i })).not.toBeVisible();
  });

  test('can create and delete a project', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const projectName = `E2E Project ${Date.now()}`;

    await page.getByRole('button', { name: /\+ new project/i }).click();
    await expect(page.getByRole('heading', { name: /new project/i })).toBeVisible();

    await page.getByPlaceholder(/johnson kitchen/i).fill(projectName);
    await page.getByTitle('Project type').selectOption('residential_remodel');
    await page.getByPlaceholder('0', { exact: true }).fill('100000');

    await page.getByRole('button', { name: /save|create/i }).click();

    await expect(page.getByRole('heading', { name: /new project/i })).not.toBeVisible();
    await expect(page.getByText(projectName)).toBeVisible({ timeout: 10000 });

    // Hover the card to reveal the delete button
    const card = page.locator('a').filter({ hasText: projectName });
    await card.hover();
    await card.getByTitle('Delete project').click();

    await expect(page.getByRole('heading', { name: /delete project/i })).toBeVisible();
    await page.getByRole('button', { name: /^delete$/i }).click();

    // Wait for the confirm modal to close, then check the card is gone
    await expect(page.getByRole('heading', { name: /delete project/i })).not.toBeVisible({ timeout: 10000 });
    await expect(page.locator('a').filter({ hasText: projectName })).not.toBeVisible({ timeout: 10000 });
  });

  test('can edit a project name', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const projectName = `Edit Test ${Date.now()}`;

    // Create
    await page.getByRole('button', { name: /\+ new project/i }).click();
    await page.getByPlaceholder(/johnson kitchen/i).fill(projectName);
    await page.getByTitle('Project type').selectOption('kitchen_bath');
    await page.getByPlaceholder('0', { exact: true }).fill('50000');
    await page.getByRole('button', { name: /save|create/i }).click();
    await expect(page.getByText(projectName)).toBeVisible({ timeout: 10000 });

    // Edit
    const card = page.locator('a').filter({ hasText: projectName });
    await card.hover();
    await card.getByTitle('Edit project').click();

    await expect(page.getByRole('heading', { name: /edit project/i })).toBeVisible();
    const nameInput = page.getByPlaceholder(/johnson kitchen/i);
    await nameInput.clear();
    const updatedName = `${projectName} UPDATED`;
    await nameInput.fill(updatedName);

    await page.getByRole('button', { name: /save|update/i }).click();
    await expect(page.getByRole('heading', { name: /edit project/i })).not.toBeVisible();
    await expect(page.getByText(updatedName)).toBeVisible({ timeout: 10000 });

    // Cleanup
    const updatedCard = page.locator('a').filter({ hasText: updatedName });
    await updatedCard.hover();
    await updatedCard.getByTitle('Delete project').click();
    await page.getByRole('button', { name: /^delete$/i }).click();
    await expect(page.getByRole('heading', { name: /delete project/i })).not.toBeVisible({ timeout: 10000 });
  });

  test('Kanban View link navigates to kanban page', async ({ page }) => {
    await page.goto('/projects');

    await expect(page.getByRole('link', { name: /kanban view/i })).toBeVisible();
    await page.getByRole('link', { name: /kanban view/i }).click();
    await expect(page).toHaveURL(/\/projects\/kanban/);
  });

  test('project card links to project detail', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const firstCard = page.locator('a[href^="/projects/"]').first();
    if ((await firstCard.count()) === 0) return; // no projects to click

    const href = await firstCard.getAttribute('href');
    await firstCard.click();
    await expect(page).toHaveURL(new RegExp(href!.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  });

  test('status chart renders when projects exist', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForLoadState('networkidle');

    const hasProjects = await page.locator('a[href^="/projects/"]').count();
    if (hasProjects === 0) return;

    await expect(page.getByText(/projects by status/i)).toBeVisible();
  });
});
