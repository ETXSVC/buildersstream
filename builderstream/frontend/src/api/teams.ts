import { apiClient } from './client';

export interface TeamMember {
  id: string;
  user: string;
  user_full_name: string;
  user_email: string;
  role: 'lead' | 'member';
  created_at: string;
}

export interface Team {
  id: string;
  name: string;
  description: string;
  member_count: number;
  members?: TeamMember[];
  created_at: string;
  updated_at?: string;
}

export const fetchTeams = (): Promise<Team[]> =>
  apiClient.get('/api/v1/teams/').then((r) => r.data.results ?? r.data);

export const fetchTeam = (id: string): Promise<Team> =>
  apiClient.get(`/api/v1/teams/${id}/`).then((r) => r.data);

export const createTeam = (data: { name: string; description?: string }): Promise<Team> =>
  apiClient.post('/api/v1/teams/', data).then((r) => r.data);

export const updateTeam = (id: string, data: { name?: string; description?: string }): Promise<Team> =>
  apiClient.patch(`/api/v1/teams/${id}/`, data).then((r) => r.data);

export const deleteTeam = (id: string): Promise<void> =>
  apiClient.delete(`/api/v1/teams/${id}/`).then(() => undefined);

export const addTeamMember = (teamId: string, userId: string, role: 'lead' | 'member' = 'member'): Promise<TeamMember> =>
  apiClient.post(`/api/v1/teams/${teamId}/add-member/`, { user_id: userId, role }).then((r) => r.data);

export const removeTeamMember = (teamId: string, userId: string): Promise<void> =>
  apiClient.delete(`/api/v1/teams/${teamId}/remove-member/${userId}/`).then(() => undefined);
