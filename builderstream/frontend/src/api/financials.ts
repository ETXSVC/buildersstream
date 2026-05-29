import { apiClient } from '@/api/client';
import type {
  Invoice, Budget, ChangeOrder, PurchaseOrder, Expense,
  JobCostSummary, CashFlowMonth, ListResponse,
} from '@/types/financials';

export async function fetchInvoices(params: Record<string, string> = {}): Promise<ListResponse<Invoice>> {
  const { data } = await apiClient.get<ListResponse<Invoice>>('/api/v1/financials/invoices/', { params });
  return data;
}

export async function createInvoice(payload: Record<string, unknown>): Promise<Invoice> {
  const { data } = await apiClient.post<Invoice>('/api/v1/financials/invoices/', payload);
  return data;
}

export async function updateInvoice(id: string, payload: Record<string, unknown>): Promise<Invoice> {
  const { data } = await apiClient.patch<Invoice>(`/api/v1/financials/invoices/${id}/`, payload);
  return data;
}

export async function deleteInvoice(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/financials/invoices/${id}/`);
}

export async function fetchBudgets(params: Record<string, string> = {}): Promise<ListResponse<Budget>> {
  const { data } = await apiClient.get<ListResponse<Budget>>('/api/v1/financials/budgets/', { params });
  return data;
}

export async function fetchChangeOrders(params: Record<string, string> = {}): Promise<ListResponse<ChangeOrder>> {
  const { data } = await apiClient.get<ListResponse<ChangeOrder>>('/api/v1/financials/change-orders/', { params });
  return data;
}

export async function fetchPurchaseOrders(params: Record<string, string> = {}): Promise<ListResponse<PurchaseOrder>> {
  const { data } = await apiClient.get<ListResponse<PurchaseOrder>>('/api/v1/financials/purchase-orders/', { params });
  return data;
}

export async function fetchExpenses(params: Record<string, string> = {}): Promise<ListResponse<Expense>> {
  const { data } = await apiClient.get<ListResponse<Expense>>('/api/v1/financials/expenses/', { params });
  return data;
}

export async function createExpense(payload: Record<string, unknown>): Promise<Expense> {
  const { data } = await apiClient.post<Expense>('/api/v1/financials/expenses/', payload);
  return data;
}

/** Download AIA G702 or G703 PDF as a Blob. form = 'g702' | 'g703' */
export async function downloadAiaPdf(invoiceId: string, form: 'g702' | 'g703' = 'g702'): Promise<Blob> {
  const { data } = await apiClient.get(
    `/api/v1/financials/invoices/${invoiceId}/generate-aia/`,
    { params: { form }, responseType: 'blob' },
  );
  return data;
}

/** Download standard invoice PDF as a Blob. */
export async function downloadInvoicePdf(invoiceId: string): Promise<Blob> {
  const { data } = await apiClient.get(
    `/api/v1/financials/invoices/${invoiceId}/export-pdf/`,
    { responseType: 'blob' },
  );
  return data;
}

export async function updateExpense(id: string, payload: Record<string, unknown>): Promise<Expense> {
  const { data } = await apiClient.patch<Expense>(`/api/v1/financials/expenses/${id}/`, payload);
  return data;
}

export async function deleteExpense(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/financials/expenses/${id}/`);
}

export async function createChangeOrder(payload: Record<string, unknown>): Promise<ChangeOrder> {
  const { data } = await apiClient.post<ChangeOrder>('/api/v1/financials/change-orders/', payload);
  return data;
}

export async function updateChangeOrder(id: string, payload: Record<string, unknown>): Promise<ChangeOrder> {
  const { data } = await apiClient.patch<ChangeOrder>(`/api/v1/financials/change-orders/${id}/`, payload);
  return data;
}

export async function deleteChangeOrder(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/financials/change-orders/${id}/`);
}

export async function createPurchaseOrder(payload: Record<string, unknown>): Promise<PurchaseOrder> {
  const { data } = await apiClient.post<PurchaseOrder>('/api/v1/financials/purchase-orders/', payload);
  return data;
}

export async function updatePurchaseOrder(id: string, payload: Record<string, unknown>): Promise<PurchaseOrder> {
  const { data } = await apiClient.patch<PurchaseOrder>(`/api/v1/financials/purchase-orders/${id}/`, payload);
  return data;
}

export async function deletePurchaseOrder(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/financials/purchase-orders/${id}/`);
}

export async function fetchJobCostReport(projectId: string): Promise<JobCostSummary> {
  const { data } = await apiClient.get<JobCostSummary>('/api/v1/financials/reports/job-cost/', {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchCashFlowReport(months = 6): Promise<CashFlowMonth[]> {
  const { data } = await apiClient.get<CashFlowMonth[]>('/api/v1/financials/reports/cash-flow/', {
    params: { months: String(months) },
  });
  return data;
}
