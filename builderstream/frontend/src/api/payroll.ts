import { apiClient } from './client';
import type { Employee, PayRun, CertifiedPayroll, WorkforceSummary, ListResponse } from '@/types/payroll';

export const fetchPayRuns = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<PayRun>>('/api/v1/payroll/payroll-runs/', { params }).then((r) => r.data);

export const createPayRun = (payload: Record<string, unknown>) =>
  apiClient.post<PayRun>('/api/v1/payroll/payroll-runs/', payload).then((r) => r.data);

export const processPayRun = (id: string) =>
  apiClient.post<PayRun>(`/api/v1/payroll/payroll-runs/${id}/process/`).then((r) => r.data);

export const approvePayRun = (id: string) =>
  apiClient.post<PayRun>(`/api/v1/payroll/payroll-runs/${id}/approve/`).then((r) => r.data);

export const markPayRunPaid = (id: string, payDate?: string) =>
  apiClient.post<PayRun>(`/api/v1/payroll/payroll-runs/${id}/mark-paid/`, payDate ? { pay_date: payDate } : {}).then((r) => r.data);

export const voidPayRun = (id: string) =>
  apiClient.post<PayRun>(`/api/v1/payroll/payroll-runs/${id}/void/`).then((r) => r.data);

export const fetchCertifiedPayrolls = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<CertifiedPayroll>>('/api/v1/payroll/certified-reports/', { params }).then((r) => r.data);

export const submitCertifiedPayroll = (id: string) =>
  apiClient.post<CertifiedPayroll>(`/api/v1/payroll/certified-reports/${id}/submit/`).then((r) => r.data);

export const fetchWorkforceSummary = async (): Promise<WorkforceSummary> => {
  // Compute workforce summary from the employees list
  const { data } = await apiClient.get<ListResponse<Employee>>('/api/v1/payroll/employees/', {
    params: { page_size: '500' },
  });
  const employees = data.results;
  const active = employees.filter((e) => e.is_active);
  const rates = active
    .map((e) => parseFloat(e.base_hourly_rate))
    .filter((r) => !isNaN(r) && r > 0);
  const avgRate = rates.length ? rates.reduce((a, b) => a + b, 0) / rates.length : null;
  return {
    total_workers: employees.length,
    active_this_week: active.length,
    total_hours_this_week: 0,
    overtime_hours_this_week: 0,
    avg_hourly_rate: avgRate,
    labor_cost_this_week: 0,
  };
};

export const fetchEmployees = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Employee>>('/api/v1/payroll/employees/', { params }).then((r) => r.data);

export const createEmployee = (payload: Record<string, unknown>) =>
  apiClient.post<Employee>('/api/v1/payroll/employees/', payload).then((r) => r.data);

export const updateEmployee = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Employee>(`/api/v1/payroll/employees/${id}/`, payload).then((r) => r.data);
