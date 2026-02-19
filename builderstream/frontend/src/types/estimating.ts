export type EstimateStatus = 'draft' | 'in_review' | 'approved' | 'rejected' | 'sent_to_client';
export type ProposalStatus = 'draft' | 'sent' | 'viewed' | 'signed' | 'expired' | 'rejected';

export interface CostItem {
  id: string;
  name: string;
  unit: string;
  cost: string;
  base_price: string;
  client_price: string;
  markup_percent: string;
  is_active: boolean;
}

export interface Estimate {
  id: string;
  project: string | null;
  project_name: string | null;
  lead: string | null;
  lead_title: string | null;
  name: string;
  estimate_number: string;
  status: EstimateStatus;
  subtotal: string;
  tax_rate: string;
  tax_amount: string;
  total: string;
  valid_until: string | null;
  created_by_name: string | null;
  approved_by_name: string | null;
  approved_at: string | null;
  created_at: string;
  section_count: number;
  line_item_count: number;
}

export interface EstimateSection {
  id: string;
  estimate: string;
  name: string;
  description: string | null;
  sort_order: number;
  subtotal: string;
  line_items: EstimateLineItem[];
}

export interface EstimateLineItem {
  id: string;
  section: string;
  description: string;
  quantity: string;
  unit: string;
  unit_cost: string;
  unit_price: string;
  line_total: string;
  is_taxable: boolean;
  sort_order: number;
}

export interface Proposal {
  id: string;
  estimate: string;
  estimate_name: string;
  estimate_number: string;
  project: string | null;
  project_name: string | null;
  lead: string | null;
  lead_title: string | null;
  client: string;
  client_name: string;
  proposal_number: string;
  status: ProposalStatus;
  total: string;
  sent_at: string | null;
  sent_to_email: string | null;
  viewed_at: string | null;
  view_count: number;
  signed_at: string | null;
  signed_by_name: string | null;
  is_signed: boolean;
  valid_until: string | null;
  created_at: string;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const ESTIMATE_STATUS_COLORS: Record<EstimateStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  in_review: 'bg-purple-100 text-purple-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  sent_to_client: 'bg-blue-100 text-blue-700',
};

export const ESTIMATE_STATUS_LABELS: Record<EstimateStatus, string> = {
  draft: 'Draft',
  in_review: 'In Review',
  approved: 'Approved',
  rejected: 'Rejected',
  sent_to_client: 'Sent to Client',
};

export const PROPOSAL_STATUS_COLORS: Record<ProposalStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  sent: 'bg-blue-100 text-blue-700',
  viewed: 'bg-purple-100 text-purple-700',
  signed: 'bg-green-100 text-green-700',
  expired: 'bg-slate-100 text-slate-500',
  rejected: 'bg-red-100 text-red-700',
};
