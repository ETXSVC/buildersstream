import { apiClient } from '@/api/client';
import type { Document, DocumentFolder, RFI, Submittal, Photo, ListResponse } from '@/types/documents';

export async function fetchFolders(params: Record<string, string> = {}): Promise<ListResponse<DocumentFolder>> {
  const { data } = await apiClient.get<ListResponse<DocumentFolder>>('/api/v1/documents/folders/', { params });
  return data;
}

export async function fetchDocuments(params: Record<string, string> = {}): Promise<ListResponse<Document>> {
  const { data } = await apiClient.get<ListResponse<Document>>('/api/v1/documents/documents/', { params });
  return data;
}

export async function fetchRFIs(params: Record<string, string> = {}): Promise<ListResponse<RFI>> {
  const { data } = await apiClient.get<ListResponse<RFI>>('/api/v1/documents/rfis/', { params });
  return data;
}

export async function fetchSubmittals(params: Record<string, string> = {}): Promise<ListResponse<Submittal>> {
  const { data } = await apiClient.get<ListResponse<Submittal>>('/api/v1/documents/submittals/', { params });
  return data;
}

export async function fetchPhotos(params: Record<string, string> = {}): Promise<ListResponse<Photo>> {
  const { data } = await apiClient.get<ListResponse<Photo>>('/api/v1/documents/photos/', { params });
  return data;
}
