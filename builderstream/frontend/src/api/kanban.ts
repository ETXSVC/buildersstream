import { apiClient } from '@/api/client';

export interface KanbanProject {
  id: string;
  project_number: string;
  name: string;
  client_name: string | null;
  project_manager_name: string | null;
  health_status: 'green' | 'yellow' | 'red' | null;
  health_score: number | null;
  estimated_value: string | null;
  start_date: string | null;
  estimated_completion: string | null;
  updated_at: string;
}

export interface KanbanColumn {
  status: string;
  label: string;
  color: string;
  count: number;
  projects: KanbanProject[];
}

export interface KanbanBoardResponse {
  columns: KanbanColumn[];
}

export async function fetchKanbanBoard(showAll = false): Promise<KanbanBoardResponse> {
  const { data } = await apiClient.get<KanbanBoardResponse>('/api/v1/kanban/', {
    params: showAll ? { show_all: 'true' } : {},
  });
  return data;
}
