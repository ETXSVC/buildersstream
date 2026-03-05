import { apiClient } from './client';

export interface Comment {
  id: string;
  project: string;
  parent: string | null;
  author: string | null;
  author_name: string;
  body: string;
  is_edited: boolean;
  edited_at: string | null;
  is_deleted: boolean;
  replies: Comment[];
  created_at: string;
  updated_at: string;
}

export async function fetchComments(projectId: string): Promise<Comment[]> {
  const { data } = await apiClient.get('/api/v1/project-comments/', { params: { project: projectId } });
  return data.results ?? data;
}

export async function createComment(payload: { project: string; body: string; parent?: string }): Promise<Comment> {
  const { data } = await apiClient.post('/api/v1/project-comments/', payload);
  return data;
}

export async function updateComment(id: string, body: string): Promise<Comment> {
  const { data } = await apiClient.patch(`/api/v1/project-comments/${id}/`, { body });
  return data;
}

export async function deleteComment(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/project-comments/${id}/`);
}
