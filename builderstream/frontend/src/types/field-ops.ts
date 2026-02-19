export interface TimeEntry {
  id: string;
  employee: string;
  employee_name: string;
  project: string | null;
  project_name: string | null;
  cost_code: string | null;
  cost_code_name: string | null;
  clock_in: string;
  clock_out: string | null;
  total_hours: string | null;
  overtime_hours: string;
  entry_type: 'clock' | 'manual';
  status: 'pending' | 'approved' | 'rejected';
  notes: string | null;
  is_within_geofence: boolean | null;
  created_at: string;
}

export interface DailyLog {
  id: string;
  project: string;
  project_name: string;
  log_date: string;
  status: 'draft' | 'submitted' | 'approved';
  weather_conditions: Record<string, unknown>;
  work_performed: string;
  delay_reason: string | null;
  manpower_count: number;
  created_by: string;
  created_by_name: string;
  created_at: string;
}

export interface ExpenseEntry {
  id: string;
  employee: string;
  employee_name: string;
  project: string | null;
  project_name: string | null;
  category: string;
  amount: string;
  description: string;
  receipt_file_key: string | null;
  mileage: string | null;
  status: 'pending' | 'approved' | 'rejected';
  incurred_date: string;
  created_at: string;
}

export interface TimesheetSummary {
  employee_id: string;
  employee_name: string;
  week_start: string;
  week_end: string;
  regular_hours: string;
  overtime_hours: string;
  total_hours: string;
  entries: TimeEntry[];
}

export interface TimeEntryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TimeEntry[];
}

export interface DailyLogListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: DailyLog[];
}

export const EXPENSE_CATEGORIES: Record<string, string> = {
  MATERIALS: 'Materials',
  TOOLS: 'Tools & Equipment',
  FUEL: 'Fuel & Mileage',
  MEALS: 'Meals',
  LODGING: 'Lodging',
  PERMITS: 'Permits & Fees',
  SUBCONTRACTOR: 'Subcontractor',
  OTHER: 'Other',
};
