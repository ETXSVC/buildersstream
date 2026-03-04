import { apiClient } from '@/api/client';
import type { TimeEntry, TimeEntryListResponse, DailyLog, DailyLogListResponse, ExpenseEntry, TimesheetSummary } from '@/types/field-ops';

export async function clockIn(projectId?: string, latitude?: number, longitude?: number): Promise<TimeEntry> {
  const { data } = await apiClient.post<TimeEntry>('/api/v1/field-ops/time-entries/clock-in/', {
    project: projectId,
    latitude,
    longitude,
  });
  return data;
}

export async function clockOut(entryId: string, latitude?: number, longitude?: number): Promise<TimeEntry> {
  const { data } = await apiClient.post<TimeEntry>(`/api/v1/field-ops/time-entries/${entryId}/clock-out/`, {
    latitude,
    longitude,
  });
  return data;
}

export async function fetchTimeEntries(params: Record<string, string> = {}): Promise<TimeEntryListResponse> {
  const { data } = await apiClient.get<TimeEntryListResponse>('/api/v1/field-ops/time-entries/', { params });
  return data;
}

export const createManualEntry = (payload: Record<string, unknown>) =>
  apiClient.post<TimeEntry>('/api/v1/field-ops/time-entries/', payload).then((r) => r.data);

export const approveTimeEntry = (id: string) =>
  apiClient.post<TimeEntry>(`/api/v1/field-ops/time-entries/${id}/approve/`).then((r) => r.data);

export const rejectTimeEntry = (id: string) =>
  apiClient.post<TimeEntry>(`/api/v1/field-ops/time-entries/${id}/reject/`).then((r) => r.data);

export async function fetchDailyLogs(params: Record<string, string> = {}): Promise<DailyLogListResponse> {
  const { data } = await apiClient.get<DailyLogListResponse>('/api/v1/field-ops/daily-logs/', { params });
  return data;
}

export const createDailyLog = (payload: Record<string, unknown>) =>
  apiClient.post<DailyLog>('/api/v1/field-ops/daily-logs/', payload).then((r) => r.data);

export async function submitDailyLog(logId: string): Promise<DailyLog> {
  const { data } = await apiClient.post<DailyLog>(`/api/v1/field-ops/daily-logs/${logId}/submit/`);
  return data;
}

export const approveDailyLog = (id: string) =>
  apiClient.post<DailyLog>(`/api/v1/field-ops/daily-logs/${id}/approve/`).then((r) => r.data);

interface TimesheetRow {
  user_id: string;
  user_name: string;
  project_id: string;
  project_name: string;
  total_hours: number;
  overtime_hours: number;
  regular_hours: number;
  week_start: string | null;
}

export async function fetchTimesheetSummary(weekStart?: string): Promise<TimesheetSummary> {
  const params = weekStart ? { week_start: weekStart } : {};
  const { data } = await apiClient.get<{ results: TimesheetRow[]; count: number }>(
    '/api/v1/field-ops/timesheets/summary/', { params }
  );
  // Aggregate per-project rows into a single weekly total
  const rows = data.results;
  const total = rows.reduce((acc, r) => acc + r.total_hours, 0);
  const ot = rows.reduce((acc, r) => acc + r.overtime_hours, 0);
  return {
    employee_id: rows[0]?.user_id ?? '',
    employee_name: rows[0]?.user_name ?? '',
    week_start: rows[0]?.week_start ?? weekStart ?? '',
    week_end: '',
    regular_hours: String((total - ot).toFixed(2)),
    overtime_hours: String(ot.toFixed(2)),
    total_hours: String(total.toFixed(2)),
    entries: [],
  };
}

export async function getOpenTimeEntry(): Promise<TimeEntry | null> {
  const { data } = await apiClient.get<TimeEntryListResponse>('/api/v1/field-ops/time-entries/', {
    params: { clock_out__isnull: 'true', status: 'pending' },
  });
  return data.results[0] ?? null;
}

export interface ExpenseListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ExpenseEntry[];
}

export async function fetchExpenses(params: Record<string, string> = {}): Promise<ExpenseListResponse> {
  const { data } = await apiClient.get<ExpenseListResponse>('/api/v1/field-ops/expenses/', { params });
  return data;
}

export const createExpense = (payload: Record<string, unknown>) =>
  apiClient.post<ExpenseEntry>('/api/v1/field-ops/expenses/', payload).then((r) => r.data);

export const approveExpense = (id: string) =>
  apiClient.post<ExpenseEntry>(`/api/v1/field-ops/expenses/${id}/approve/`).then((r) => r.data);

export const rejectExpense = (id: string) =>
  apiClient.post<ExpenseEntry>(`/api/v1/field-ops/expenses/${id}/reject/`).then((r) => r.data);
