import { Page } from '@playwright/test';

export const TEST_USER = {
  email: 'admin@builderstream.com',
  password: 'demo1234!',
};

export async function login(page: Page) {
  await page.goto('/login');
  await page.waitForSelector('#email', { state: 'visible' });
  await page.locator('#email').fill(TEST_USER.email);
  await page.locator('#password').fill(TEST_USER.password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await page.waitForURL(/dashboard|overview/, { timeout: 15000 });
}

/** Save auth state so it can be reused across tests. */
export async function loginAndSave(page: Page, storagePath: string) {
  await login(page);
  await page.context().storageState({ path: storagePath });
}
