import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchEstimates, fetchEstimate, fetchProposals, sendProposal } from '@/api/estimating';

const STALE = 30_000;

export function useEstimates(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['estimating', 'estimates', params],
    queryFn: () => fetchEstimates(params),
    staleTime: STALE,
  });
}

export function useEstimate(id: string | undefined) {
  return useQuery({
    queryKey: ['estimating', 'estimate', id],
    queryFn: () => fetchEstimate(id!),
    enabled: !!id,
    staleTime: STALE,
  });
}

export function useProposals(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['estimating', 'proposals', params],
    queryFn: () => fetchProposals(params),
    staleTime: STALE,
  });
}

export function useSendProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, email }: { id: string; email?: string }) => sendProposal(id, email),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating', 'proposals'] }),
  });
}
