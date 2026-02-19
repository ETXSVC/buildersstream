export type InspectionStatus = 'scheduled' | 'in_progress' | 'passed' | 'failed' | 'requires_action';
export type DeficiencyStatus = 'open' | 'in_progress' | 'resolved' | 'verified';
export type DeficiencySeverity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentSeverity = 'near_miss' | 'first_aid' | 'recordable' | 'lost_time' | 'fatality';

export interface Inspection {
  id: string;
  inspection_number: string;
  project: string | null;
  project_name: string | null;
  inspection_type: string;
  status: InspectionStatus;
  scheduled_date: string | null;
  completed_date: string | null;
  inspector_name: string | null;
  score: number | null;
  passed: boolean | null;
  deficiency_count: number;
  notes: string | null;
  created_at: string;
}

export interface Deficiency {
  id: string;
  inspection: string | null;
  inspection_number: string | null;
  project: string | null;
  project_name: string | null;
  title: string;
  description: string;
  severity: DeficiencySeverity;
  status: DeficiencyStatus;
  assigned_to_name: string | null;
  due_date: string | null;
  resolved_date: string | null;
  created_at: string;
}

export interface SafetyIncident {
  id: string;
  incident_number: string;
  project: string | null;
  project_name: string | null;
  incident_date: string;
  incident_type: string;
  severity: IncidentSeverity;
  description: string;
  injured_party: string | null;
  injuries_count: number;
  reported_by_name: string | null;
  osha_recordable: boolean;
  is_resolved: boolean;
  root_cause: string | null;
  corrective_action: string | null;
  created_at: string;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const INSPECTION_STATUS_COLORS: Record<InspectionStatus, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-purple-100 text-purple-700',
  passed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  requires_action: 'bg-amber-100 text-amber-700',
};

export const DEFICIENCY_STATUS_COLORS: Record<DeficiencyStatus, string> = {
  open: 'bg-red-100 text-red-700',
  in_progress: 'bg-amber-100 text-amber-700',
  resolved: 'bg-blue-100 text-blue-700',
  verified: 'bg-green-100 text-green-700',
};

export const SEVERITY_COLORS: Record<DeficiencySeverity, string> = {
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-amber-100 text-amber-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

export const INCIDENT_SEVERITY_COLORS: Record<IncidentSeverity, string> = {
  near_miss: 'bg-slate-100 text-slate-600',
  first_aid: 'bg-amber-100 text-amber-700',
  recordable: 'bg-orange-100 text-orange-700',
  lost_time: 'bg-red-100 text-red-700',
  fatality: 'bg-red-200 text-red-900',
};
