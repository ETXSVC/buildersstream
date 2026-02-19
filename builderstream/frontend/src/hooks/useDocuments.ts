import { useQuery } from '@tanstack/react-query';
import { fetchFolders, fetchDocuments, fetchRFIs, fetchSubmittals, fetchPhotos } from '@/api/documents';

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

export function useSubmittals(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'submittals', params],
    queryFn: () => fetchSubmittals(params),
    staleTime: STALE,
  });
}

export function usePhotos(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['documents', 'photos', params],
    queryFn: () => fetchPhotos(params),
    staleTime: STALE,
  });
}
