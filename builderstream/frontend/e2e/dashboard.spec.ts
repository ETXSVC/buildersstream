import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

// All dashboard tests run authenticated via the pre-saved storage state.
test.use({ storageState: STORAGE_STATE });

test.describe('Dashboard', () => {
  test('loads dashboard with widgets', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // The WidgetCard component renders widget titles in <h3> elements.
    await expect(
      page.getByRole('heading', { name: /project overview/i }).first(),
    ).toBeVisible();

    await expect(
      page.getByRole('heading', { name: /financial summary/i }).first(),
    ).toBeVisible();
  });

  test('shows project metrics', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // ProjectMetricsWidget renders MetricCard labels as small text nodes.
    await expect(page.getByText(/total projects/i).first()).toBeVisible();
    await expect(page.getByText(/active/i).first()).toBeVisible();
  });

  test('can refresh dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // Wait for the dashboard to finish loading before trying to refresh
    await expect(
      page.getByRole('heading', { name: /project overview/i }).first(),
    ).toBeVisible();

    // The refresh button has title="Refresh dashboard" and no visible label
    const refreshButton = page.getByTitle('Refresh dashboard');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();

    // After clicking refresh the page should not show an error state
    await expect(
      page.getByText(/failed to load dashboard/i),
    ).not.toBeVisible();
  });

  test('subnav shows Analytics link', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

    // DashboardPage renders <SubNav items={[{label:'Dashboard',...},{label:'Analytics',...}]} />
    // SubNav produces <NavLink> elements which render as <a> tags.
    const analyticsLink = page.getByRole('link', { name: 'Analytics' }).first();
    await expect(analyticsLink).toBeVisible();
  });
});
