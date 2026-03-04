import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchEstimates, fetchEstimate, fetchProposals, fetchCostItems,
  createEstimate, updateEstimate, deleteEstimate,
  approveEstimate, copyEstimate, generateProposal,
  updateProposal, deleteProposal, sendProposal,
} from '@/api/estimating';

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

export function useCreateEstimate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createEstimate(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useUpdateEstimate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateEstimate(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useDeleteEstimate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteEstimate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useApproveEstimate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => approveEstimate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useCopyEstimate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => copyEstimate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useGenerateProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ estimateId, payload }: { estimateId: string; payload: Record<string, unknown> }) =>
      generateProposal(estimateId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useProposals(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['estimating', 'proposals', params],
    queryFn: () => fetchProposals(params),
    staleTime: STALE,
  });
}

export function useUpdateProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateProposal(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useDeleteProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteProposal(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useSendProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, email }: { id: string; email?: string }) => sendProposal(id, email),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['estimating'] }),
  });
}

export function useCostItems(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['estimating', 'cost-items', params],
    queryFn: () => fetchCostItems(params),
    staleTime: 60_000,
  });
}
