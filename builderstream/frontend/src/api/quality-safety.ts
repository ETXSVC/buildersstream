import { apiClient } from './client';
import type { Inspection, Deficiency, SafetyIncident, ListResponse } from '@/types/quality-safety';

export const fetchInspections = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Inspection>>('/api/v1/quality-safety/inspections/', { params }).then((r) => r.data);

export const createInspection = (payload: Record<string, unknown>) =>
  apiClient.post<Inspection>('/api/v1/quality-safety/inspections/', payload).then((r) => r.data);

export const updateInspection = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Inspection>(`/api/v1/quality-safety/inspections/${id}/`, payload).then((r) => r.data);

export const deleteInspection = (id: string) =>
  apiClient.delete(`/api/v1/quality-safety/inspections/${id}/`);

export const fetchDeficiencies = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Deficiency>>('/api/v1/quality-safety/deficiencies/', { params }).then((r) => r.data);

export const fetchSafetyIncidents = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<SafetyIncident>>('/api/v1/quality-safety/incidents/', { params }).then((r) => r.data);

export const createSafetyIncident = (payload: Record<string, unknown>) =>
  apiClient.post<SafetyIncident>('/api/v1/quality-safety/incidents/', payload).then((r) => r.data);

export const updateSafetyIncident = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<SafetyIncident>(`/api/v1/quality-safety/incidents/${id}/`, payload).then((r) => r.data);

export const deleteSafetyIncident = (id: string) =>
  apiClient.delete(`/api/v1/quality-safety/incidents/${id}/`);
