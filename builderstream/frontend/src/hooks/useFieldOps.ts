import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchTimeEntries,
  fetchDailyLogs,
  fetchTimesheetSummary,
  getOpenTimeEntry,
  clockIn,
  clockOut,
} from '@/api/field-ops';

export function useOpenTimeEntry() {
  return useQuery({
    queryKey: ['field-ops', 'open-entry'],
    queryFn: getOpenTimeEntry,
    staleTime: 10 * 1000,
    refetchInterval: 30 * 1000, // poll every 30s while page open
  });
}

export function useTimeEntries(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['field-ops', 'time-entries', params],
    queryFn: () => fetchTimeEntries(params),
    staleTime: 30 * 1000,
  });
}

export function useDailyLogs(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['field-ops', 'daily-logs', params],
    queryFn: () => fetchDailyLogs(params),
    staleTime: 30 * 1000,
  });
}

export function useTimesheetSummary(weekStart?: string) {
  return useQuery({
    queryKey: ['field-ops', 'timesheet', weekStart],
    queryFn: () => fetchTimesheetSummary(weekStart),
    staleTime: 60 * 1000,
  });
}

export function useClockIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, latitude, longitude }: { projectId?: string; latitude?: number; longitude?: number }) =>
      clockIn(projectId, latitude, longitude),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['field-ops'] });
    },
  });
}

export function useClockOut() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ entryId, latitude, longitude }: { entryId: string; latitude?: number; longitude?: number }) =>
      clockOut(entryId, latitude, longitude),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['field-ops'] });
    },
  });
}
