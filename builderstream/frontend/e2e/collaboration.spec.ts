import { test, expect } from '@playwright/test';
import { STORAGE_STATE } from '../playwright.config';

test.use({ storageState: STORAGE_STATE });

test('loads collaboration page', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // "Team Chat" header is always rendered in the sidebar (static text)
  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 15000 });
});

test('can open create channel modal', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // Wait for Team Chat header to confirm page rendered
  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 15000 });

  // Click the + button with title "New channel" in the Team Chat header
  const newChannelBtn = page.locator('button[title="New channel"]').first();
  await expect(newChannelBtn).toBeVisible({ timeout: 10000 });
  await newChannelBtn.click();

  // Modal should appear with "Create Channel" heading
  await expect(page.getByRole('heading', { name: 'Create Channel' })).toBeVisible();

  // Channel name input has placeholder "e.g. general" (no htmlFor association)
  await expect(page.getByPlaceholder('e.g. general')).toBeVisible();
});

test('create channel modal closes on cancel', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // Wait for Team Chat header to confirm page rendered
  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 15000 });

  // Open the modal
  const newChannelBtn = page.locator('button[title="New channel"]').first();
  await expect(newChannelBtn).toBeVisible({ timeout: 10000 });
  await newChannelBtn.click();

  await expect(page.getByRole('heading', { name: 'Create Channel' })).toBeVisible();

  // Click Cancel
  await page.getByRole('button', { name: 'Cancel' }).click();

  // Modal should no longer be visible
  await expect(page.getByRole('heading', { name: 'Create Channel' })).not.toBeVisible();
});

test('can create a channel', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // Wait for Team Chat header to confirm page rendered
  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 15000 });

  // Open the Create Channel modal
  const newChannelBtn = page.locator('button[title="New channel"]').first();
  await expect(newChannelBtn).toBeVisible({ timeout: 10000 });
  await newChannelBtn.click();

  await expect(page.getByRole('heading', { name: 'Create Channel' })).toBeVisible();

  // Use a unique name to avoid conflicts with previously created channels
  const uniqueName = `e2e-${Date.now()}`;
  await page.getByPlaceholder('e.g. general').fill(uniqueName);

  // Submit the form
  await page.getByRole('button', { name: 'Create' }).click();

  // Modal should close after submission
  await expect(page.getByRole('heading', { name: 'Create Channel' })).not.toBeVisible({ timeout: 10000 });
});

test('subnav shows Issues link', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // SubNav renders NavLinks — find the "Issues" link
  await expect(page.getByRole('link', { name: 'Issues' })).toBeVisible({ timeout: 10000 });
});

test('can open new DM modal', async ({ page }) => {
  await page.goto('/collaboration');
  await page.locator('aside').first().waitFor({ state: 'visible', timeout: 30000 });

  // Wait for Team Chat header to confirm page rendered
  await expect(page.getByText('Team Chat')).toBeVisible({ timeout: 15000 });

  // The + button next to "Direct Messages" section
  const dmPlusBtn = page.locator('button[title="New direct message"]').first();
  await expect(dmPlusBtn).toBeVisible({ timeout: 10000 });
  await dmPlusBtn.scrollIntoViewIfNeeded();
  await dmPlusBtn.click();

  // Modal with "New Direct Message" heading should appear
  await expect(page.getByRole('heading', { name: 'New Direct Message' })).toBeVisible();
});
