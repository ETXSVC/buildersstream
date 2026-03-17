import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

// ── Sidebar ────────────────────────────────────────────────────────────────

test('sidebar has 8 top-level nav items', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();

  await expect(sidebar.getByText('Overview')).toBeVisible();
  await expect(sidebar.getByText('Projects')).toBeVisible();
  await expect(sidebar.getByText('Sales')).toBeVisible();
  await expect(sidebar.getByText('Operations')).toBeVisible();
  await expect(sidebar.getByText('Finance & HR')).toBeVisible();
  await expect(sidebar.getByText('Company')).toBeVisible();
  await expect(sidebar.getByText('Team Messaging')).toBeVisible();
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

test('sidebar Overview link navigates to dashboard', async ({ page }) => {
  await page.goto('/projects');

  const sidebar = page.locator('aside').first();
  await sidebar.getByText('Overview').click();
  await expect(page).toHaveURL(/\/dashboard/);
});

test('sidebar Company link navigates to company page', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();
  await sidebar.getByText('Company').click();
  await expect(page).toHaveURL(/\/company/);
  await expect(page.getByRole('heading', { name: 'Company' })).toBeVisible();
});

test('sidebar Team Messaging link navigates to collaboration', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();
  await sidebar.getByText('Team Messaging').click();
  await expect(page).toHaveURL(/\/collaboration/);
});

test('Settings opens branding page', async ({ page }) => {
  await page.goto('/dashboard');

  const sidebar = page.locator('aside').first();
  await sidebar.getByText('Settings').click();

  await expect(page).toHaveURL(/\/settings/);
});

test('active nav item is visually highlighted', async ({ page }) => {
  await page.goto('/projects');
  await page.waitForLoadState('networkidle');

  // The active NavLink gets 'bs-sidebar-link-active' class
  const activeLink = page.locator('aside').first().locator('a.bs-sidebar-link-active');
  await expect(activeLink).toBeVisible();
  await expect(activeLink).toHaveText('Projects');
});

// ── Header ─────────────────────────────────────────────────────────────────

test('header shows company name', async ({ page }) => {
  await page.goto('/dashboard');

  // The branding name or fallback "BuilderStream" is in the header
  const header = page.locator('header').first();
  await expect(header).toBeVisible();
  // Either the org branding name or the default site name
  const siteName = header.locator('span').filter({ hasText: /\w+/ }).first();
  await expect(siteName).toBeVisible();
});

test('header shows logged-in user name', async ({ page }) => {
  await page.goto('/dashboard');

  const header = page.locator('header').first();
  // User name is rendered as "{first_name} {last_name}" in a <span>
  await expect(header.locator('span').filter({ hasText: /\S+ \S+/ }).first()).toBeVisible();
});

test('header has Sign out button', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page.getByRole('button', { name: /sign out/i })).toBeVisible();
});

test('header has notification bell', async ({ page }) => {
  await page.goto('/dashboard');

  // NotificationBell renders a button with a bell icon
  const header = page.locator('header').first();
  await expect(header.locator('button').first()).toBeVisible();
});

test('header search button is visible', async ({ page }) => {
  await page.goto('/dashboard');

  const header = page.locator('header').first();
  await expect(header.getByText('Search')).toBeVisible();
});

test('command palette opens on search button click', async ({ page }) => {
  await page.goto('/dashboard');

  // Click the Search button in the header
  const header = page.locator('header').first();
  await header.getByText('Search').click();

  // Command palette renders an input
  await expect(page.getByPlaceholder(/search/i).last()).toBeVisible({ timeout: 5000 });
});

// ── Direct URL navigation ───────────────────────────────────────────────────

test('direct navigation to /projects renders projects page', async ({ page }) => {
  await page.goto('/projects');
  await expect(page.getByRole('heading', { name: 'Projects' })).toBeVisible();
});

test('direct navigation to /crm renders CRM page', async ({ page }) => {
  await page.goto('/crm');
  await expect(page.getByText(/contacts|leads|pipeline/i).first()).toBeVisible();
});

test('direct navigation to /financials renders financials page', async ({ page }) => {
  await page.goto('/financials');
  await expect(page.getByText(/invoices|revenue|financials/i).first()).toBeVisible();
});

test('direct navigation to /field-ops renders field ops page', async ({ page }) => {
  await page.goto('/field-ops');
  await expect(page.getByText(/field ops|time entries|crew/i).first()).toBeVisible();
});

test('direct navigation to /company renders company page', async ({ page }) => {
  await page.goto('/company');
  await expect(page.getByRole('heading', { name: 'Company' })).toBeVisible();
});

test('direct navigation to /settings/branding renders settings', async ({ page }) => {
  await page.goto('/settings/branding');
  await expect(page.getByText(/branding|white.?label|company name/i).first()).toBeVisible();
});

// ── Company page ────────────────────────────────────────────────────────────

test('Company page loads', async ({ page }) => {
  await page.goto('/company');

  await expect(page.getByRole('heading', { name: 'Company' })).toBeVisible();
  await expect(page.getByText('Total Employees')).toBeVisible();
  await expect(page.getByText('Total Contractors')).toBeVisible();
  await expect(page.getByText('Total Workforce')).toBeVisible();
  await expect(page.getByText('Team Members').first()).toBeVisible();
  await expect(page.getByText('Teams').first()).toBeVisible();
});

// ── Team Messaging (collaboration) ──────────────────────────────────────────

test('Team page loads collaboration', async ({ page }) => {
  await page.goto('/collaboration');
  await page.waitForLoadState('networkidle');

  await expect(page.getByText('Channels', { exact: false })).toBeVisible({ timeout: 10000 });
});

test('collaboration page has Team Chat sidebar header', async ({ page }) => {
  await page.goto('/collaboration');
  await page.waitForLoadState('networkidle');

  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 10000 });
});

test('collaboration page has DM section', async ({ page }) => {
  await page.goto('/collaboration');
  await page.waitForLoadState('networkidle');

  await expect(page.getByText('Direct Messages', { exact: false })).toBeVisible({ timeout: 10000 });
});

test('collaboration page has Archived section', async ({ page }) => {
  await page.goto('/collaboration');
  await page.waitForLoadState('networkidle');

  await expect(page.getByText('Archived', { exact: false })).toBeVisible({ timeout: 10000 });
});

// ── Sign out ────────────────────────────────────────────────────────────────

test('sign out redirects to login', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: /sign out/i }).first().click();
  await page.waitForURL(/\/login/, { timeout: 15000 });
  expect(page.url()).toContain('/login');
});
