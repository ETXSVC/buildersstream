import { useQuery } from '@tanstack/react-query';
import {
  fetchInvoices, fetchBudgets, fetchChangeOrders,
  fetchPurchaseOrders, fetchJobCostReport, fetchCashFlowReport,
} from '@/api/financials';

const STALE = 30_000;

export function useInvoices(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'invoices', params],
    queryFn: () => fetchInvoices(params),
    staleTime: STALE,
  });
}

export function useBudgets(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'budgets', params],
    queryFn: () => fetchBudgets(params),
    staleTime: STALE,
  });
}

export function useChangeOrders(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'change-orders', params],
    queryFn: () => fetchChangeOrders(params),
    staleTime: STALE,
  });
}

export function usePurchaseOrders(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'purchase-orders', params],
    queryFn: () => fetchPurchaseOrders(params),
    staleTime: STALE,
  });
}

export function useJobCostReport(projectId: string | undefined) {
  return useQuery({
    queryKey: ['financials', 'job-cost', projectId],
    queryFn: () => fetchJobCostReport(projectId!),
    enabled: !!projectId,
    staleTime: STALE,
  });
}

export function useCashFlowReport(months = 6) {
  return useQuery({
    queryKey: ['financials', 'cash-flow', months],
    queryFn: () => fetchCashFlowReport(months),
    staleTime: STALE,
  });
}
