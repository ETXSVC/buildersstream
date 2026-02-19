export type ProjectStatus =
  | 'lead'
  | 'prospect'
  | 'estimate'
  | 'proposal'
  | 'contract'
  | 'production'
  | 'punch_list'
  | 'closeout'
  | 'completed'
  | 'canceled';

export type HealthStatus = 'green' | 'yellow' | 'red';

export interface ProjectTeamMember {
  user_id: string;
  name: string;
  email: string;
  role: string;
}

export interface ProjectMilestone {
  id: string;
  name: string;
  due_date: string | null;
  completed_date: string | null;
  status: string;
  is_overdue: boolean;
}

export interface Project {
  id: string;
  project_number: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  client: string | null;
  client_name: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  estimated_value: string | null;
  actual_value: string | null;
  start_date: string | null;
  target_completion: string | null;
  actual_completion: string | null;
  health_score: number | null;
  health_status: HealthStatus | null;
  project_manager: string | null;
  project_manager_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  milestones: ProjectMilestone[];
  team: ProjectTeamMember[];
  action_items_count: number;
  open_rfis_count: number;
  pending_submittals_count: number;
}

export interface ProjectListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Project[];
}

export interface ProjectFilters {
  status?: ProjectStatus;
  health_status?: HealthStatus;
  search?: string;
  page?: number;
}

export const STATUS_LABELS: Record<ProjectStatus, string> = {
  lead: 'Lead',
  prospect: 'Prospect',
  estimate: 'Estimate',
  proposal: 'Proposal',
  contract: 'Contract',
  production: 'Production',
  punch_list: 'Punch List',
  closeout: 'Closeout',
  completed: 'Completed',
  canceled: 'Canceled',
};

export const STATUS_COLORS: Record<ProjectStatus, string> = {
  lead: 'bg-slate-100 text-slate-700',
  prospect: 'bg-blue-100 text-blue-700',
  estimate: 'bg-purple-100 text-purple-700',
  proposal: 'bg-indigo-100 text-indigo-700',
  contract: 'bg-cyan-100 text-cyan-700',
  production: 'bg-amber-100 text-amber-700',
  punch_list: 'bg-orange-100 text-orange-700',
  closeout: 'bg-teal-100 text-teal-700',
  completed: 'bg-green-100 text-green-700',
  canceled: 'bg-red-100 text-red-700',
};

export const HEALTH_COLORS: Record<HealthStatus, string> = {
  green: 'bg-green-500',
  yellow: 'bg-yellow-400',
  red: 'bg-red-500',
};
