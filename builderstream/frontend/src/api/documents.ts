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

export const createRFI = (payload: Record<string, unknown>) =>
  apiClient.post<RFI>('/api/v1/documents/rfis/', payload).then((r) => r.data);

export const updateRFI = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<RFI>(`/api/v1/documents/rfis/${id}/`, payload).then((r) => r.data);

export const deleteRFI = (id: string) =>
  apiClient.delete(`/api/v1/documents/rfis/${id}/`);

export async function fetchSubmittals(params: Record<string, string> = {}): Promise<ListResponse<Submittal>> {
  const { data } = await apiClient.get<ListResponse<Submittal>>('/api/v1/documents/submittals/', { params });
  return data;
}

export const createSubmittal = (payload: Record<string, unknown>) =>
  apiClient.post<Submittal>('/api/v1/documents/submittals/', payload).then((r) => r.data);

export const updateSubmittal = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Submittal>(`/api/v1/documents/submittals/${id}/`, payload).then((r) => r.data);

export const deleteSubmittal = (id: string) =>
  apiClient.delete(`/api/v1/documents/submittals/${id}/`);

export async function fetchPhotos(params: Record<string, string> = {}): Promise<ListResponse<Photo>> {
  const { data } = await apiClient.get<ListResponse<Photo>>('/api/v1/documents/photos/', { params });
  return data;
}
