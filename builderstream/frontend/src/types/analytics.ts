export interface KPIData {
  revenue_mtd: number;
  revenue_ytd: number;
  revenue_target_ytd: number | null;
  revenue_variance_percent: number | null;
  active_projects: number;
  projects_on_schedule: number;
  projects_over_budget: number;
  open_bids: number;
  win_rate: number | null;
  avg_project_margin: number | null;
  overdue_invoices_count: number;
  overdue_invoices_amount: number;
  open_rfis: number;
  pending_submittals: number;
  field_hours_this_week: number;
  safety_incidents_ytd: number;
}

export interface ReportSummary {
  id: string;
  name: string;
  report_type: string;
  description: string | null;
  last_run_at: string | null;
  created_by_name: string | null;
  created_at: string;
}

export interface ExportJob {
  id: string;
  report: string;
  report_name: string;
  format: 'pdf' | 'excel' | 'csv';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_url: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const REPORT_TYPE_LABELS: Record<string, string> = {
  job_cost: 'Job Cost Report',
  cash_flow: 'Cash Flow Report',
  payroll: 'Payroll Report',
  safety: 'Safety Report',
  productivity: 'Productivity Report',
  aging_ar: 'Aging AR Report',
  wip: 'WIP Schedule',
};
