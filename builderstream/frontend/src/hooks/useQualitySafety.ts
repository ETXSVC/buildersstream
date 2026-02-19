import { useQuery } from '@tanstack/react-query';
import { fetchInspections, fetchDeficiencies, fetchSafetyIncidents } from '@/api/quality-safety';

export const useInspections = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['inspections', params],
    queryFn: () => fetchInspections(params),
    staleTime: 30_000,
  });

export const useDeficiencies = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['deficiencies', params],
    queryFn: () => fetchDeficiencies(params),
    staleTime: 30_000,
  });

export const useSafetyIncidents = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['safety-incidents', params],
    queryFn: () => fetchSafetyIncidents(params),
    staleTime: 30_000,
  });
