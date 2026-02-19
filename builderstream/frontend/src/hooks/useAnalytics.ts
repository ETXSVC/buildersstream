import { useQuery } from '@tanstack/react-query';
import { fetchKPIs, fetchReportSummary, fetchReports } from '@/api/analytics';

export function useKPIs() {
  return useQuery({
    queryKey: ['analytics', 'kpis'],
    queryFn: fetchKPIs,
    staleTime: 60_000,
    refetchOnWindowFocus: true,
  });
}

export function useReportSummary() {
  return useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: fetchReportSummary,
    staleTime: 60_000,
  });
}

export function useReports(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['analytics', 'reports', params],
    queryFn: () => fetchReports(params),
    staleTime: 60_000,
  });
}
