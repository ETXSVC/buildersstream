import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchInspections, fetchDeficiencies, fetchSafetyIncidents,
  createInspection, updateInspection, deleteInspection,
  createSafetyIncident, updateSafetyIncident, deleteSafetyIncident,
} from '@/api/quality-safety';

export const useInspections = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['inspections', params],
    queryFn: () => fetchInspections(params),
    staleTime: 30_000,
  });

export function useCreateInspection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createInspection(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inspections'] }),
  });
}

export function useUpdateInspection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateInspection(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inspections'] }),
  });
}

export function useDeleteInspection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteInspection(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inspections'] }),
  });
}

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

export function useCreateSafetyIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createSafetyIncident(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['safety-incidents'] }),
  });
}

export function useUpdateSafetyIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateSafetyIncident(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['safety-incidents'] }),
  });
}

export function useDeleteSafetyIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteSafetyIncident(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['safety-incidents'] }),
  });
}
