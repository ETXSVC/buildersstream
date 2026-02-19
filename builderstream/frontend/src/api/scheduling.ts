import { apiClient } from '@/api/client';
import type { Task, Crew, Equipment, GanttData, CrewAvailability, ListResponse } from '@/types/scheduling';

export async function fetchTasks(params: Record<string, string> = {}): Promise<ListResponse<Task>> {
  const { data } = await apiClient.get<ListResponse<Task>>('/api/v1/scheduling/tasks/', { params });
  return data;
}

export async function fetchGanttData(projectId: string): Promise<GanttData> {
  const { data } = await apiClient.get<GanttData>('/api/v1/scheduling/tasks/gantt/', {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchCrews(params: Record<string, string> = {}): Promise<ListResponse<Crew>> {
  const { data } = await apiClient.get<ListResponse<Crew>>('/api/v1/scheduling/crews/', { params });
  return data;
}

export async function fetchCrewAvailability(): Promise<CrewAvailability[]> {
  const { data } = await apiClient.get<CrewAvailability[]>('/api/v1/scheduling/crews/availability/');
  return data;
}

export async function fetchEquipment(params: Record<string, string> = {}): Promise<ListResponse<Equipment>> {
  const { data } = await apiClient.get<ListResponse<Equipment>>('/api/v1/scheduling/equipment/', { params });
  return data;
}
