import { apiClient } from './client';

export interface IssueType {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  default_priority: string;
  sla_response_hours: number;
  sla_resolution_hours: number;
  is_active: boolean;
  created_at: string;
}

export interface IssueListItem {
  id: string;
  number: string;
  title: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'open' | 'in_progress' | 'pending' | 'resolved' | 'closed';
  issue_type: string | null;
  issue_type_name: string | null;
  assignee: string | null;
  assignee_name: string | null;
  project: string | null;
  client: string | null;
  sla_response_due_at: string | null;
  sla_resolution_due_at: string | null;
  sla_response_met: boolean | null;
  sla_resolution_met: boolean | null;
  is_sla_response_breached: boolean;
  is_sla_resolution_breached: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface IssueComment {
  id: string;
  issue: string;
  parent: string | null;
  content: string;
  is_edited: boolean;
  edited_at: string | null;
  is_internal: boolean;
  author_name: string | null;
  replies: IssueComment[];
  created_at: string;
}

export interface IssueDetail extends IssueListItem {
  description: string;
  reporter: string | null;
  reporter_name: string | null;
  first_responded_at: string | null;
  resolved_at: string | null;
  custom_fields: Record<string, unknown>;
  comments: IssueComment[];
  attachments: Array<{
    id: string;
    filename: string;
    file_size: number;
    content_type: string;
    file_key: string;
    created_at: string;
  }>;
}

export interface SLACompliance {
  total_issues: number;
  response_sla: { met: number; breached: number; compliance_pct: number };
  resolution_sla: { met: number; breached: number; compliance_pct: number };
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
}

export async function fetchIssues(params?: Record<string, string>): Promise<{ results: IssueListItem[]; count: number }> {
  const { data } = await apiClient.get('/api/v1/issue-tracking/issues/', { params });
  return data;
}

export async function fetchIssue(id: string): Promise<IssueDetail> {
  const { data } = await apiClient.get(`/api/v1/issue-tracking/issues/${id}/`);
  return data;
}

export async function createIssue(payload: {
  title: string;
  description?: string;
  issue_type?: string;
  priority?: string;
  project?: string;
  client?: string;
  assignee?: string;
  tags?: string[];
}): Promise<IssueDetail> {
  const { data } = await apiClient.post('/api/v1/issue-tracking/issues/', payload);
  return data;
}

export async function updateIssue(id: string, payload: Partial<IssueDetail>): Promise<IssueDetail> {
  const { data } = await apiClient.patch(`/api/v1/issue-tracking/issues/${id}/`, payload);
  return data;
}

export async function transitionIssueStatus(id: string, newStatus: string): Promise<IssueDetail> {
  const { data } = await apiClient.post(`/api/v1/issue-tracking/issues/${id}/transition/`, { status: newStatus });
  return data.issue;
}

export async function addIssueComment(
  id: string,
  payload: { content: string; parent?: string; is_internal?: boolean }
): Promise<IssueComment> {
  const { data } = await apiClient.post(`/api/v1/issue-tracking/issues/${id}/add-comment/`, payload);
  return data;
}

export async function fetchIssueTypes(): Promise<IssueType[]> {
  const { data } = await apiClient.get('/api/v1/issue-tracking/issue-types/');
  return Array.isArray(data) ? data : data.results ?? [];
}

export async function fetchSLACompliance(): Promise<SLACompliance> {
  const { data } = await apiClient.get('/api/v1/issue-tracking/reports/sla-compliance/');
  return data;
}
