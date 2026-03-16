import { test as setup } from '@playwright/test';
import { login } from './helpers/auth';
import { STORAGE_STATE } from '../playwright.config';

setup('authenticate', async ({ page }) => {
  await login(page);
  await page.context().storageState({ path: STORAGE_STATE });
});
