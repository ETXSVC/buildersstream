export type Urgency = 'hot' | 'warm' | 'cold';
export type ProjectType =
  | 'custom_home'
  | 'residential_remodel'
  | 'kitchen_bath'
  | 'addition'
  | 'commercial'
  | 'tenant_improvement'
  | 'roofing'
  | 'siding'
  | 'other';

export interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  mobile_phone: string | null;
  job_title: string | null;
  company_name: string | null;
  lead_score: number;
  tags: string[];
  notes: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Lead {
  id: string;
  contact: string | null;
  contact_name: string | null;
  pipeline_stage: string | null;
  stage_name: string | null;
  stage_color: string | null;
  project_type: ProjectType | null;
  estimated_value: string | null;
  estimated_start: string | null;
  urgency: Urgency;
  description: string | null;
  assigned_to: string | null;
  assigned_to_name: string | null;
  last_contacted_at: string | null;
  next_follow_up: string | null;
  created_at: string;
  updated_at: string;
}

export interface PipelineStage {
  id: string;
  name: string;
  order: number;
  color: string | null;
  is_won_stage: boolean;
  is_lost_stage: boolean;
  lead_count?: number;
}

export interface ContactListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Contact[];
}

export interface LeadListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

export const URGENCY_COLORS: Record<Urgency, string> = {
  hot: 'bg-red-100 text-red-700',
  warm: 'bg-amber-100 text-amber-700',
  cold: 'bg-blue-100 text-blue-700',
};

export const URGENCY_LABELS: Record<Urgency, string> = {
  hot: 'Hot',
  warm: 'Warm',
  cold: 'Cold',
};

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  custom_home: 'Custom Home',
  residential_remodel: 'Residential Remodel',
  kitchen_bath: 'Kitchen & Bath',
  addition: 'Addition',
  commercial: 'Commercial',
  tenant_improvement: 'Tenant Improvement',
  roofing: 'Roofing',
  siding: 'Siding',
  other: 'Other',
};
