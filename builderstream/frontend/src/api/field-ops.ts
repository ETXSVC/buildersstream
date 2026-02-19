import { apiClient } from '@/api/client';
import type { TimeEntry, TimeEntryListResponse, DailyLog, DailyLogListResponse, TimesheetSummary } from '@/types/field-ops';

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

export async function fetchDailyLogs(params: Record<string, string> = {}): Promise<DailyLogListResponse> {
  const { data } = await apiClient.get<DailyLogListResponse>('/api/v1/field-ops/daily-logs/', { params });
  return data;
}

export async function fetchTimesheetSummary(weekStart?: string): Promise<TimesheetSummary> {
  const params = weekStart ? { week_start: weekStart } : {};
  const { data } = await apiClient.get<TimesheetSummary>('/api/v1/field-ops/timesheets/summary/', { params });
  return data;
}

export async function submitDailyLog(logId: string): Promise<DailyLog> {
  const { data } = await apiClient.post<DailyLog>(`/api/v1/field-ops/daily-logs/${logId}/submit/`);
  return data;
}

export async function getOpenTimeEntry(): Promise<TimeEntry | null> {
  const { data } = await apiClient.get<TimeEntryListResponse>('/api/v1/field-ops/time-entries/', {
    params: { clock_out__isnull: 'true', status: 'pending' },
  });
  return data.results[0] ?? null;
}
