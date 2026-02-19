import { apiClient } from '@/api/client';
import type {
  Invoice, Budget, ChangeOrder, PurchaseOrder, Expense,
  JobCostSummary, CashFlowMonth, ListResponse,
} from '@/types/financials';

export async function fetchInvoices(params: Record<string, string> = {}): Promise<ListResponse<Invoice>> {
  const { data } = await apiClient.get<ListResponse<Invoice>>('/api/v1/financials/invoices/', { params });
  return data;
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
