import { test, expect } from '@playwright/test'
import { STORAGE_STATE } from '../playwright.config'

test.use({ storageState: STORAGE_STATE })

test.describe('Financials page', () => {
  test('loads financials page with KPI cards', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    // The KpiCard label text is in the DOM as mixed-case; CSS uppercases it visually.
    // We match by the DOM text (case-insensitive) via role="button" on the card divs.
    await expect(
      page.locator('[role="button"]').filter({ hasText: /total invoiced/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /outstanding/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /overdue invoices/i }).first(),
    ).toBeVisible()
    await expect(
      page.locator('[role="button"]').filter({ hasText: /total expenses/i }).first(),
    ).toBeVisible()
  })

  test('KPI card Total Invoiced navigates to invoices tab', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    const totalInvoicedCard = page.locator('[role="button"]').filter({ hasText: /total invoiced/i }).first()
    await expect(totalInvoicedCard).toBeVisible({ timeout: 15000 })
    await totalInvoicedCard.click()

    // The Invoices tab button should be active (amber background)
    const invoicesTab = page.getByRole('button', { name: /^invoices$/i })
    await expect(invoicesTab).toBeVisible()
    await expect(invoicesTab).toHaveClass(/bg-blue-500/)
  })

  test('KPI card Total Expenses navigates to expenses tab', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    const totalExpensesCard = page.locator('[role="button"]').filter({ hasText: /total expenses/i }).first()
    await expect(totalExpensesCard).toBeVisible({ timeout: 15000 })
    await totalExpensesCard.click()

    // The Expenses tab button should be active (amber background)
    const expensesTab = page.getByRole('button', { name: /^expenses$/i })
    await expect(expensesTab).toBeVisible()
    await expect(expensesTab).toHaveClass(/bg-blue-500/)
  })

  test('tab switching works', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    // Click "Expenses" tab
    await page.getByRole('button', { name: /^expenses$/i }).click()
    // Expenses tab is now active
    await expect(page.getByRole('button', { name: /^expenses$/i })).toHaveClass(/bg-blue-500/)
    // Expenses table heading should be visible
    await expect(page.getByRole('columnheader', { name: /amount/i }).first()).toBeVisible()

    // Click "Change Orders" tab
    await page.getByRole('button', { name: /change orders/i }).click()
    await expect(page.getByRole('button', { name: /change orders/i })).toHaveClass(/bg-blue-500/)
    // Change Orders table heading should be visible
    await expect(page.getByRole('columnheader', { name: /co #/i }).first()).toBeVisible()
  })

  test('subnav shows Payroll link', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    // SubNav renders NavLinks which become <a> elements
    await expect(page.getByRole('link', { name: 'Payroll' })).toBeVisible()
  })

  test('can open new invoice modal', async ({ page }) => {
    await page.goto('/financials')
    await page.waitForLoadState('networkidle')

    // Ensure we are on the Invoices tab (it's the default, but click to be sure)
    await page.getByRole('button', { name: /^invoices$/i }).click()

    // Click the "+ New Invoice" button
    await page.getByRole('button', { name: /new invoice/i }).click()

    // The modal should appear with the heading "New Invoice"
    await expect(page.getByRole('heading', { name: /new invoice/i })).toBeVisible()
    // The modal form should include a Status field
    await expect(page.getByTitle('Status').first()).toBeVisible()
  })
})
