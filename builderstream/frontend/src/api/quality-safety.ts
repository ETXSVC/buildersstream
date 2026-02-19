import { apiClient } from './client';
import type { Inspection, Deficiency, SafetyIncident, ListResponse } from '@/types/quality-safety';

export const fetchInspections = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Inspection>>('/api/v1/quality-safety/inspections/', { params }).then((r) => r.data);

export const fetchDeficiencies = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Deficiency>>('/api/v1/quality-safety/deficiencies/', { params }).then((r) => r.data);

export const fetchSafetyIncidents = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<SafetyIncident>>('/api/v1/quality-safety/incidents/', { params }).then((r) => r.data);
