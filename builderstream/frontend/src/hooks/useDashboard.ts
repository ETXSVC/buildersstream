import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchDashboard,
  fetchDashboardLayout,
  updateDashboardLayout,
} from '@/api/dashboard';

/**
 * Fetch main dashboard data with 60-second cache
 * (matches backend Redis cache duration)
 */
export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
    staleTime: 60 * 1000, // 60 seconds
    refetchOnWindowFocus: true,
  });
}

/**
 * Fetch dashboard layout configuration
 */
export function useDashboardLayout() {
  return useQuery({
    queryKey: ['dashboard', 'layout'],
    queryFn: fetchDashboardLayout,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Update dashboard layout with optimistic updates
 */
export function useUpdateDashboardLayout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateDashboardLayout,
    onSuccess: (data) => {
      // Update cached layout
      queryClient.setQueryData(['dashboard', 'layout'], data);
    },
  });
}

/**
 * Refresh dashboard data manually
 */
export function useRefreshDashboard() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };
}
