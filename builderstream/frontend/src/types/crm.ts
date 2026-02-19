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
  created_at: string;
}

export interface Lead {
  id: string;
  title: string;
  contact: string | null;
  contact_name: string | null;
  company: string | null;
  company_name: string | null;
  stage: string | null;
  stage_name: string | null;
  status: 'active' | 'won' | 'lost' | 'on_hold';
  lead_score: number;
  estimated_value: string | null;
  source: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to: string | null;
  assigned_to_name: string | null;
  expected_close_date: string | null;
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

export const LEAD_STATUS_COLORS: Record<Lead['status'], string> = {
  active: 'bg-blue-100 text-blue-700',
  won: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700',
  on_hold: 'bg-slate-100 text-slate-700',
};

export const PRIORITY_COLORS: Record<Lead['priority'], string> = {
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
};

export const SOURCE_LABELS: Record<string, string> = {
  referral: 'Referral',
  website: 'Website',
  social_media: 'Social Media',
  cold_call: 'Cold Call',
  trade_show: 'Trade Show',
  repeat_client: 'Repeat Client',
  other: 'Other',
};
