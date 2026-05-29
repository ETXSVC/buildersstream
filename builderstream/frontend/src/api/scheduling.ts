import { apiClient } from '@/api/client';
import type { Task, Crew, Equipment, GanttData, CrewAvailability, ListResponse } from '@/types/scheduling';

export interface OrgMember {
  id: string;
  user: string;
  user_email: string;
  user_full_name: string;
  role: string;
}

export async function fetchOrgMembers(): Promise<OrgMember[]> {
  const { data } = await apiClient.get<ListResponse<OrgMember>>('/api/v1/tenants/memberships/', {
    params: { page_size: '200' },
  });
  return data.results;
}

export async function fetchTasks(params: Record<string, string> = {}): Promise<ListResponse<Task>> {
  const { data } = await apiClient.get<ListResponse<Task>>('/api/v1/scheduling/tasks/', { params });
  return data;
}

export async function createTask(payload: Record<string, unknown>): Promise<Task> {
  const { data } = await apiClient.post<Task>('/api/v1/scheduling/tasks/', payload);
  return data;
}

export async function updateTask(id: string, payload: Record<string, unknown>): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/api/v1/scheduling/tasks/${id}/`, payload);
  return data;
}

export async function deleteTask(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/scheduling/tasks/${id}/`);
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

export async function createCrew(payload: Record<string, unknown>): Promise<Crew> {
  const { data } = await apiClient.post<Crew>('/api/v1/scheduling/crews/', payload);
  return data;
}

export async function updateCrew(id: string, payload: Record<string, unknown>): Promise<Crew> {
  const { data } = await apiClient.patch<Crew>(`/api/v1/scheduling/crews/${id}/`, payload);
  return data;
}

export async function deleteCrew(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/scheduling/crews/${id}/`);
}

export async function fetchCrewAvailability(): Promise<CrewAvailability[]> {
  const { data } = await apiClient.get<CrewAvailability[]>('/api/v1/scheduling/crews/availability/');
  return data;
}

export async function fetchEquipment(params: Record<string, string> = {}): Promise<ListResponse<Equipment>> {
  const { data } = await apiClient.get<ListResponse<Equipment>>('/api/v1/scheduling/equipment/', { params });
  return data;
}

export async function createEquipment(payload: Record<string, unknown>): Promise<Equipment> {
  const { data } = await apiClient.post<Equipment>('/api/v1/scheduling/equipment/', payload);
  return data;
}

export async function updateEquipment(id: string, payload: Record<string, unknown>): Promise<Equipment> {
  const { data } = await apiClient.patch<Equipment>(`/api/v1/scheduling/equipment/${id}/`, payload);
  return data;
}

export async function deleteEquipment(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/scheduling/equipment/${id}/`);
}

export async function patchTaskDates(
  id: string,
  payload: { start_date?: string; end_date?: string; estimated_hours?: number }
): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/api/v1/scheduling/tasks/${id}/dates/`, payload);
  return data;
}
