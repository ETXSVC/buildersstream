import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchPayRuns, createPayRun, processPayRun, approvePayRun, markPayRunPaid, voidPayRun,
  fetchCertifiedPayrolls, submitCertifiedPayroll,
  fetchWorkforceSummary,
  fetchEmployees, createEmployee, updateEmployee,
} from '@/api/payroll';

const KEY = 'pay-runs';
const CERT_KEY = 'certified-payrolls';

export const usePayRuns = (params?: Record<string, string>) =>
  useQuery({
    queryKey: [KEY, params],
    queryFn: () => fetchPayRuns(params),
    staleTime: 30_000,
  });

export function useCreatePayRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createPayRun(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useProcessPayRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => processPayRun(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useApprovePayRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => approvePayRun(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useMarkPayRunPaid() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payDate }: { id: string; payDate?: string }) => markPayRunPaid(id, payDate),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useVoidPayRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => voidPayRun(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export const useCertifiedPayrolls = (params?: Record<string, string>) =>
  useQuery({
    queryKey: [CERT_KEY, params],
    queryFn: () => fetchCertifiedPayrolls(params),
    staleTime: 30_000,
  });

export function useSubmitCertifiedPayroll() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => submitCertifiedPayroll(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CERT_KEY] }),
  });
}

export const useWorkforceSummary = () =>
  useQuery({
    queryKey: ['workforce-summary'],
    queryFn: fetchWorkforceSummary,
    staleTime: 60_000,
  });

const EMP_KEY = 'employees';

export const useEmployees = (params?: Record<string, string>) =>
  useQuery({
    queryKey: [EMP_KEY, params],
    queryFn: () => fetchEmployees(params),
    staleTime: 30_000,
  });

export function useCreateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createEmployee(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [EMP_KEY] }),
  });
}

export function useUpdateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      updateEmployee(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [EMP_KEY] }),
  });
}
