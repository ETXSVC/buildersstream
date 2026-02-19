import { apiClient } from '@/api/client';
import type { Project, ProjectDetail, ProjectListResponse, ProjectFilters } from '@/types/projects';

export async function fetchProjects(filters: ProjectFilters = {}): Promise<ProjectListResponse> {
  const params = new URLSearchParams();
  if (filters.status) params.set('status', filters.status);
  if (filters.health_status) params.set('health_status', filters.health_status);
  if (filters.search) params.set('search', filters.search);
  if (filters.page) params.set('page', String(filters.page));
  const { data } = await apiClient.get<ProjectListResponse>('/api/v1/projects/', { params });
  return data;
}

export async function fetchProject(id: string): Promise<ProjectDetail> {
  const { data } = await apiClient.get<ProjectDetail>(`/api/v1/projects/${id}/`);
  return data;
}

export async function updateProjectStatus(id: string, status: string): Promise<Project> {
  const { data } = await apiClient.post<Project>(`/api/v1/projects/${id}/transition/`, { status });
  return data;
}
