import { apiClient } from './client';
import type {
  DashboardData,
  DashboardLayout,
  DashboardLayoutPayload,
} from '@/types/dashboard';

/**
 * Fetch main dashboard data with all widgets
 */
export async function fetchDashboard(): Promise<DashboardData> {
  const { data } = await apiClient.get<DashboardData>('/api/v1/dashboard/');
  return data;
}

/**
 * Fetch user's dashboard layout configuration
 */
export async function fetchDashboardLayout(): Promise<DashboardLayout> {
  const { data } = await apiClient.get<DashboardLayout>(
    '/api/v1/dashboard/layout/',
  );
  return data;
}

/**
 * Update user's dashboard layout configuration
 */
export async function updateDashboardLayout(
  payload: DashboardLayoutPayload,
): Promise<DashboardLayout> {
  const { data } = await apiClient.put<DashboardLayout>(
    '/api/v1/dashboard/layout/',
    payload,
  );
  return data;
}
