import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchInvoices, fetchBudgets, fetchChangeOrders,
  fetchPurchaseOrders, fetchExpenses, fetchJobCostReport, fetchCashFlowReport,
  createInvoice, updateInvoice, deleteInvoice,
  createExpense, updateExpense, deleteExpense,
  createChangeOrder, updateChangeOrder, deleteChangeOrder,
  createPurchaseOrder, updatePurchaseOrder, deletePurchaseOrder,
} from '@/api/financials';

const STALE = 30_000;

export function useInvoices(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'invoices', params],
    queryFn: () => fetchInvoices(params),
    staleTime: STALE,
  });
}

export function useCreateInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createInvoice(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'invoices'] }),
  });
}

export function useUpdateInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateInvoice(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'invoices'] }),
  });
}

export function useDeleteInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteInvoice(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'invoices'] }),
  });
}

export function useBudgets(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'budgets', params],
    queryFn: () => fetchBudgets(params),
    staleTime: STALE,
  });
}

export function useExpenses(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'expenses', params],
    queryFn: () => fetchExpenses(params),
    staleTime: STALE,
  });
}

export function useCreateExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createExpense(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'expenses'] }),
  });
}

export function useUpdateExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateExpense(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'expenses'] }),
  });
}

export function useDeleteExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteExpense(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'expenses'] }),
  });
}

export function useChangeOrders(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'change-orders', params],
    queryFn: () => fetchChangeOrders(params),
    staleTime: STALE,
  });
}

export function useCreateChangeOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createChangeOrder(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'change-orders'] }),
  });
}

export function useUpdateChangeOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateChangeOrder(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'change-orders'] }),
  });
}

export function useDeleteChangeOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteChangeOrder(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'change-orders'] }),
  });
}

export function usePurchaseOrders(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['financials', 'purchase-orders', params],
    queryFn: () => fetchPurchaseOrders(params),
    staleTime: STALE,
  });
}

export function useCreatePurchaseOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createPurchaseOrder(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'purchase-orders'] }),
  });
}

export function useUpdatePurchaseOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updatePurchaseOrder(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'purchase-orders'] }),
  });
}

export function useDeletePurchaseOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deletePurchaseOrder(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['financials', 'purchase-orders'] }),
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
