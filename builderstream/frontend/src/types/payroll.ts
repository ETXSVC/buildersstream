export type PayRunStatus = 'draft' | 'processing' | 'approved' | 'paid' | 'voided';

export interface PayRun {
  id: string;
  pay_period_start: string;
  pay_period_end: string;
  pay_date: string | null;
  status: PayRunStatus;
  total_regular_hours: string;
  total_overtime_hours: string;
  total_gross_pay: string;
  total_deductions: string;
  total_net_pay: string;
  employee_count: number;
  created_by_name: string | null;
  approved_by_name: string | null;
  created_at: string;
}

export interface WorkerPaySummary {
  id: string;
  pay_run: string;
  worker_name: string;
  worker_email: string;
  regular_hours: string;
  overtime_hours: string;
  regular_rate: string;
  overtime_rate: string;
  gross_pay: string;
  deductions: string;
  net_pay: string;
}

export interface CertifiedPayroll {
  id: string;
  project: string;
  project_name: string | null;
  pay_period_start: string;
  pay_period_end: string;
  week_number: number;
  contractor_name: string;
  worker_count: number;
  total_wages: string;
  submitted: boolean;
  submitted_date: string | null;
  created_at: string;
}

export interface WorkforceSummary {
  total_workers: number;
  active_this_week: number;
  total_hours_this_week: number;
  overtime_hours_this_week: number;
  avg_hourly_rate: number | null;
  labor_cost_this_week: number;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const PAY_RUN_STATUS_COLORS: Record<PayRunStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  processing: 'bg-blue-100 text-blue-700',
  approved: 'bg-purple-100 text-purple-700',
  paid: 'bg-green-100 text-green-700',
  voided: 'bg-red-100 text-red-500',
};
