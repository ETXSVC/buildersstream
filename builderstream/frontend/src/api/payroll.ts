import { apiClient } from './client';
import type { PayRun, CertifiedPayroll, WorkforceSummary, ListResponse } from '@/types/payroll';

export const fetchPayRuns = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<PayRun>>('/api/v1/payroll/pay-runs/', { params }).then((r) => r.data);

export const fetchCertifiedPayrolls = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<CertifiedPayroll>>('/api/v1/payroll/certified-payroll/', { params }).then((r) => r.data);

export const fetchWorkforceSummary = () =>
  apiClient.get<WorkforceSummary>('/api/v1/payroll/workforce/summary/').then((r) => r.data);
