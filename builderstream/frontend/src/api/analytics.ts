import { apiClient } from '@/api/client';
import type { KPIData, ReportSummary, ExportJob, ListResponse } from '@/types/analytics';

export async function fetchKPIs(): Promise<KPIData> {
  const { data } = await apiClient.get<KPIData>('/api/v1/analytics/kpis/current/');
  return data;
}

export async function fetchReportSummary(): Promise<{ kpis: KPIData; generated_at: string }> {
  const { data } = await apiClient.get<{ kpis: KPIData; generated_at: string }>('/api/v1/analytics/summary/');
  return data;
}

export async function fetchReports(params: Record<string, string> = {}): Promise<ListResponse<ReportSummary>> {
  const { data } = await apiClient.get<ListResponse<ReportSummary>>('/api/v1/analytics/reports/', { params });
  return data;
}

export async function fetchExportJobs(params: Record<string, string> = {}): Promise<ListResponse<ExportJob>> {
  const { data } = await apiClient.get<ListResponse<ExportJob>>('/api/v1/analytics/export-jobs/', { params });
  return data;
}
