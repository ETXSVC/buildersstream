import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchFolders, fetchDocuments, fetchRFIs, fetchSubmittals, fetchPhotos,
  createRFI, updateRFI, deleteRFI,
  createSubmittal, updateSubmittal, deleteSubmittal,
} from '@/api/documents';

const STALE = 30_000;

export function useFolders(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'folders', params],
    queryFn: () => fetchFolders(params),
    staleTime: STALE,
  });
}

export function useDocuments(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'documents', params],
    queryFn: () => fetchDocuments(params),
    staleTime: STALE,
  });
}

export function useRFIs(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'rfis', params],
    queryFn: () => fetchRFIs(params),
    staleTime: STALE,
  });
}

export function useCreateRFI() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createRFI(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'rfis'] }),
  });
}

export function useUpdateRFI() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateRFI(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'rfis'] }),
  });
}

export function useDeleteRFI() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteRFI(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'rfis'] }),
  });
}

export function useSubmittals(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'submittals', params],
    queryFn: () => fetchSubmittals(params),
    staleTime: STALE,
  });
}

export function useCreateSubmittal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createSubmittal(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'submittals'] }),
  });
}

export function useUpdateSubmittal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) => updateSubmittal(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'submittals'] }),
  });
}

export function useDeleteSubmittal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteSubmittal(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', 'submittals'] }),
  });
}

export function usePhotos(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'photos', params],
    queryFn: () => fetchPhotos(params),
    staleTime: STALE,
  });
}
