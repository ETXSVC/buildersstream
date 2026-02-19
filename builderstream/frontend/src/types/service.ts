export type ServiceRequestStatus = 'new' | 'assigned' | 'in_progress' | 'on_hold' | 'completed' | 'closed';
export type ServiceRequestPriority = 'low' | 'medium' | 'high' | 'urgent';
export type WarrantyStatus = 'active' | 'expired' | 'claimed' | 'void';

export interface ServiceRequest {
  id: string;
  request_number: string;
  project: string | null;
  project_name: string | null;
  client_name: string | null;
  title: string;
  description: string;
  priority: ServiceRequestPriority;
  status: ServiceRequestStatus;
  assigned_to_name: string | null;
  scheduled_date: string | null;
  completed_date: string | null;
  estimated_hours: number | null;
  actual_hours: number | null;
  created_at: string;
}

export interface WarrantyClaim {
  id: string;
  warranty: string;
  warranty_item: string;
  project_name: string | null;
  claim_date: string;
  description: string;
  status: string;
  resolution: string | null;
  resolved_date: string | null;
  created_at: string;
}

export interface Warranty {
  id: string;
  project: string | null;
  project_name: string | null;
  item_description: string;
  warranty_type: string;
  status: WarrantyStatus;
  start_date: string;
  expiry_date: string;
  provider: string | null;
  claim_count: number;
  created_at: string;
}

export interface DispatchBoard {
  date: string;
  technicians: {
    id: string;
    name: string;
    assignments: {
      request_id: string;
      request_number: string;
      title: string;
      scheduled_time: string | null;
      priority: ServiceRequestPriority;
      status: ServiceRequestStatus;
    }[];
  }[];
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const SERVICE_STATUS_COLORS: Record<ServiceRequestStatus, string> = {
  new: 'bg-blue-100 text-blue-700',
  assigned: 'bg-purple-100 text-purple-700',
  in_progress: 'bg-amber-100 text-amber-700',
  on_hold: 'bg-slate-100 text-slate-600',
  completed: 'bg-green-100 text-green-700',
  closed: 'bg-slate-100 text-slate-500',
};

export const SERVICE_PRIORITY_COLORS: Record<ServiceRequestPriority, string> = {
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-amber-100 text-amber-700',
  urgent: 'bg-red-100 text-red-700',
};

export const WARRANTY_STATUS_COLORS: Record<WarrantyStatus, string> = {
  active: 'bg-green-100 text-green-700',
  expired: 'bg-slate-100 text-slate-500',
  claimed: 'bg-amber-100 text-amber-700',
  void: 'bg-red-100 text-red-500',
};
