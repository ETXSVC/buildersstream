import { test, expect } from '@playwright/test';
import { TEST_USER } from './helpers/auth';
import { STORAGE_STATE } from '../playwright.config';

// Unauthenticated tests — explicitly clear any inherited storageState
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('Authentication', () => {
  test('shows login page', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('#email', { state: 'visible' });

    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('logs in successfully', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('#email', { state: 'visible' });

    await page.locator('#email').fill(TEST_USER.email);
    await page.locator('#password').fill(TEST_USER.password);
    await page.getByRole('button', { name: /sign in/i }).click();

    await page.waitForURL(/dashboard|overview/, { timeout: 15000 });
    expect(page.url()).toMatch(/dashboard|overview/);
  });

  test('shows error for wrong password', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('#email', { state: 'visible' });

    await page.locator('#email').fill(TEST_USER.email);
    await page.locator('#password').fill('wrong-password-12345');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/invalid email or password/i)).toBeVisible();
  });

  test('can log out', async ({ browser }) => {
    const context = await browser.newContext({ storageState: STORAGE_STATE });
    const page = await context.newPage();

    await page.goto('/dashboard');
    await page.getByRole('button', { name: /sign out/i }).first().click();

    await page.waitForURL(/login/, { timeout: 15000 });
    expect(page.url()).toContain('/login');

    await context.close();
  });
});
