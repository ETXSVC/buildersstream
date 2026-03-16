import { apiClient } from './client';

export interface Member {
  id: string;
  user: string;
  user_email: string;
  user_full_name: string;
  organization: string;
  role: MemberRole;
  is_active: boolean;
  invited_by: string | null;
  invited_at: string | null;
  accepted_at: string | null;
  created_at: string;
}

export type MemberRole =
  | 'owner'
  | 'admin'
  | 'project_manager'
  | 'estimator'
  | 'accountant'
  | 'field_worker'
  | 'read_only';

export const ROLE_LABELS: Record<MemberRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  project_manager: 'Project Manager',
  estimator: 'Estimator',
  accountant: 'Accountant',
  field_worker: 'Field Worker',
  read_only: 'Read Only',
};

export const ROLE_COLORS: Record<MemberRole, string> = {
  owner: 'bg-purple-100 text-purple-700',
  admin: 'bg-red-100 text-red-700',
  project_manager: 'bg-blue-100 text-blue-700',
  estimator: 'bg-indigo-100 text-indigo-700',
  accountant: 'bg-green-100 text-green-700',
  field_worker: 'bg-amber-100 text-amber-700',
  read_only: 'bg-slate-100 text-slate-500',
};

export const fetchMembers = (): Promise<Member[]> =>
  apiClient.get('/api/v1/tenants/memberships/').then((r) => r.data.results ?? r.data);

export const inviteMember = (data: { email: string; role: MemberRole }): Promise<Member | { detail: string }> =>
  apiClient.post('/api/v1/tenants/memberships/invite/', data).then((r) => r.data);

export const updateMember = (id: string, data: { role?: MemberRole; is_active?: boolean }): Promise<Member> =>
  apiClient.patch(`/api/v1/tenants/memberships/${id}/`, data).then((r) => r.data);
