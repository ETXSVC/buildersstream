import { useQuery } from '@tanstack/react-query';
import { fetchTasks, fetchCrews, fetchEquipment, fetchGanttData, fetchCrewAvailability } from '@/api/scheduling';

const STALE = 30_000;

export function useTasks(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['scheduling', 'tasks', params],
    queryFn: () => fetchTasks(params),
    staleTime: STALE,
  });
}

export function useGanttData(projectId: string | undefined) {
  return useQuery({
    queryKey: ['scheduling', 'gantt', projectId],
    queryFn: () => fetchGanttData(projectId!),
    enabled: !!projectId,
    staleTime: STALE,
  });
}

export function useCrews(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['scheduling', 'crews', params],
    queryFn: () => fetchCrews(params),
    staleTime: STALE,
  });
}

export function useCrewAvailability() {
  return useQuery({
    queryKey: ['scheduling', 'crew-availability'],
    queryFn: fetchCrewAvailability,
    staleTime: STALE,
  });
}

export function useEquipment(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['scheduling', 'equipment', params],
    queryFn: () => fetchEquipment(params),
    staleTime: STALE,
  });
}
