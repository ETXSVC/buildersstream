import { test, expect } from '@playwright/test'
import { STORAGE_STATE } from '../playwright.config'

test.use({ storageState: STORAGE_STATE })

test.describe('Field Ops page', () => {
  test('loads field ops page with KPI cards', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    // KpiCard renders role="button" when onClick is provided.
    // DOM text is mixed-case ("Time Entries"); CSS uppercases it visually.
    await expect(
      page.locator('[role="button"]').filter({ hasText: /time entries/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /total hours/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /daily logs/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /pending expenses/i }).first(),
    ).toBeVisible()
  })

  test('KPI card Time Entries navigates to time entries tab', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    await page.locator('[role="button"]').filter({ hasText: /^time entries/i }).first().click()

    // The "Time Entries" tab button should now have the active (amber) class
    const timeTab = page.getByRole('button', { name: /^time entries$/i })
    await expect(timeTab).toBeVisible()
    await expect(timeTab).toHaveClass(/bg-amber-500/)
  })

  test('KPI card Daily Logs navigates to daily logs tab', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    await page.locator('[role="button"]').filter({ hasText: /^daily logs/i }).first().click()

    const dailyLogsTab = page.getByRole('button', { name: /^daily logs$/i })
    await expect(dailyLogsTab).toBeVisible()
    await expect(dailyLogsTab).toHaveClass(/bg-amber-500/)
  })

  test('KPI card Pending Expenses navigates to expenses tab', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    await page.locator('[role="button"]').filter({ hasText: /pending expenses/i }).first().click()

    const expensesTab = page.getByRole('button', { name: /^expenses$/i })
    await expect(expensesTab).toBeVisible()
    await expect(expensesTab).toHaveClass(/bg-amber-500/)
  })

  test('subnav shows Quality & Safety and Service links', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    // SubNav renders React Router NavLinks as <a> elements
    await expect(page.getByRole('link', { name: 'Quality & Safety' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Service' })).toBeVisible()
  })

  test('clock in/out button is visible', async ({ page }) => {
    await page.goto('/field-ops')
    await page.waitForLoadState('networkidle')

    // The clock status banner renders a React Router <Link> (i.e. an <a>) with
    // text "Clock In" or "Clock Out" depending on whether there is an open entry.
    const clockLink = page.getByRole('link', { name: /clock in|clock out/i })
    await expect(clockLink).toBeVisible()
  })
})
