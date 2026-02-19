import { useQuery } from '@tanstack/react-query';
import { fetchContacts, fetchLeads, fetchPipelineStages } from '@/api/crm';

export function useContacts(search?: string, page = 1) {
  return useQuery({
    queryKey: ['crm', 'contacts', { search, page }],
    queryFn: () => fetchContacts(search, page),
    staleTime: 30 * 1000,
  });
}

export function useLeads(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['crm', 'leads', params],
    queryFn: () => fetchLeads(params),
    staleTime: 30 * 1000,
  });
}

export function usePipelineStages() {
  return useQuery({
    queryKey: ['crm', 'pipeline-stages'],
    queryFn: fetchPipelineStages,
    staleTime: 5 * 60 * 1000,
  });
}
