import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const STORAGE_STATE = path.join(__dirname, 'e2e/.auth/user.json');

// Use BASE_URL env var, fall back to live site.
// For local testing: BASE_URL=http://localhost:4173 npm run test:e2e
const BASE_URL = process.env.BASE_URL ?? 'https://buildersstream.online';

export default defineConfig({
  testDir: './e2e',
  timeout: 45000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 3 : 2,
  reporter: [['html', { open: 'never' }], ['line']],
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    storageState: STORAGE_STATE,
  },
  projects: [
    {
      name: 'setup',
      testMatch: /global-setup\.ts/,
      use: { storageState: { cookies: [], origins: [] } },
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
  ],
});
