import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchTimeEntries,
  fetchDailyLogs,
  fetchTimesheetSummary,
  fetchExpenses,
  getOpenTimeEntry,
  clockIn,
  clockOut,
  createManualEntry,
  approveTimeEntry,
  rejectTimeEntry,
  createDailyLog,
  submitDailyLog,
  approveDailyLog,
  createExpense,
  approveExpense,
  rejectExpense,
} from '@/api/field-ops';

export function useOpenTimeEntry() {
  return useQuery({
    queryKey: ['field-ops', 'open-entry'],
    queryFn: getOpenTimeEntry,
    staleTime: 10 * 1000,
    refetchInterval: 30 * 1000,
  });
}

export function useTimeEntries(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['field-ops', 'time-entries', params],
    queryFn: () => fetchTimeEntries(params),
    staleTime: 30 * 1000,
  });
}

export function useCreateManualEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createManualEntry(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'time-entries'] }),
  });
}

export function useApproveTimeEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => approveTimeEntry(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'time-entries'] }),
  });
}

export function useRejectTimeEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => rejectTimeEntry(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'time-entries'] }),
  });
}

export function useDailyLogs(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['field-ops', 'daily-logs', params],
    queryFn: () => fetchDailyLogs(params),
    staleTime: 30 * 1000,
  });
}

export function useCreateDailyLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createDailyLog(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'daily-logs'] }),
  });
}

export function useSubmitDailyLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => submitDailyLog(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'daily-logs'] }),
  });
}

export function useApproveDailyLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => approveDailyLog(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'daily-logs'] }),
  });
}

export function useExpenses(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['field-ops', 'expenses', params],
    queryFn: () => fetchExpenses(params),
    staleTime: 30 * 1000,
  });
}

export function useCreateExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createExpense(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'expenses'] }),
  });
}

export function useApproveExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => approveExpense(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'expenses'] }),
  });
}

export function useRejectExpense() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => rejectExpense(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['field-ops', 'expenses'] }),
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
