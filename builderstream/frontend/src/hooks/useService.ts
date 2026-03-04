import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchServiceRequests, fetchWarranties, fetchWarrantyClaims, fetchDispatchBoard,
  createServiceRequest, updateServiceRequest, deleteServiceRequest,
  createWarranty, updateWarranty, deleteWarranty,
} from '@/api/service';

export const useServiceRequests = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['service-requests', params],
    queryFn: () => fetchServiceRequests(params),
    staleTime: 30_000,
  });

export function useCreateServiceRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createServiceRequest(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-requests'] }),
  });
}

export function useUpdateServiceRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateServiceRequest(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-requests'] }),
  });
}

export function useDeleteServiceRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteServiceRequest(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-requests'] }),
  });
}

export const useWarranties = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['warranties', params],
    queryFn: () => fetchWarranties(params),
    staleTime: 30_000,
  });

export function useCreateWarranty() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createWarranty(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['warranties'] }),
  });
}

export function useUpdateWarranty() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateWarranty(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['warranties'] }),
  });
}

export function useDeleteWarranty() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteWarranty(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['warranties'] }),
  });
}

export const useWarrantyClaims = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['warranty-claims', params],
    queryFn: () => fetchWarrantyClaims(params),
    staleTime: 30_000,
  });

export const useDispatchBoard = (date: string) =>
  useQuery({
    queryKey: ['dispatch-board', date],
    queryFn: () => fetchDispatchBoard(date),
    staleTime: 30_000,
    enabled: !!date,
  });
