import { useQuery } from '@tanstack/react-query';
import { fetchPayRuns, fetchCertifiedPayrolls, fetchWorkforceSummary } from '@/api/payroll';

export const usePayRuns = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['pay-runs', params],
    queryFn: () => fetchPayRuns(params),
    staleTime: 30_000,
  });

export const useCertifiedPayrolls = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['certified-payrolls', params],
    queryFn: () => fetchCertifiedPayrolls(params),
    staleTime: 30_000,
  });

export const useWorkforceSummary = () =>
  useQuery({
    queryKey: ['workforce-summary'],
    queryFn: fetchWorkforceSummary,
    staleTime: 60_000,
  });
