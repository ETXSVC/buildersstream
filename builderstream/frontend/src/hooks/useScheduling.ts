import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchTasks, fetchCrews, fetchEquipment, fetchGanttData, fetchCrewAvailability,
  fetchOrgMembers,
  createTask, updateTask, deleteTask,
  createCrew, updateCrew, deleteCrew,
  createEquipment, updateEquipment, deleteEquipment,
} from '@/api/scheduling';

export function useOrgMembers() {
  return useQuery({
    queryKey: ['org-members'],
    queryFn: fetchOrgMembers,
    staleTime: 60_000,
  });
}

const STALE = 30_000;

export function useTasks(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['scheduling', 'tasks', params],
    queryFn: () => fetchTasks(params),
    staleTime: STALE,
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createTask(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'tasks'] }),
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateTask(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'tasks'] }),
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteTask(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'tasks'] }),
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

export function useCreateCrew() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createCrew(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'crews'] }),
  });
}

export function useUpdateCrew() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateCrew(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'crews'] }),
  });
}

export function useDeleteCrew() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCrew(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'crews'] }),
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

export function useCreateEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createEquipment(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'equipment'] }),
  });
}

export function useUpdateEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateEquipment(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'equipment'] }),
  });
}

export function useDeleteEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteEquipment(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['scheduling', 'equipment'] }),
  });
}
