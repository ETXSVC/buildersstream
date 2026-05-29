import { apiClient } from '@/api/client';
import type { Estimate, Proposal, CostItem, ListResponse } from '@/types/estimating';

export async function fetchEstimates(params: Record<string, string> = {}): Promise<ListResponse<Estimate>> {
  const { data } = await apiClient.get<ListResponse<Estimate>>('/api/v1/estimating/estimates/', { params });
  return data;
}

export async function fetchEstimate(id: string): Promise<Estimate> {
  const { data } = await apiClient.get<Estimate>(`/api/v1/estimating/estimates/${id}/`);
  return data;
}

export const createEstimate = (payload: Record<string, unknown>) =>
  apiClient.post<Estimate>('/api/v1/estimating/estimates/', payload).then((r) => r.data);

export const updateEstimate = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Estimate>(`/api/v1/estimating/estimates/${id}/`, payload).then((r) => r.data);

export const deleteEstimate = (id: string) =>
  apiClient.delete(`/api/v1/estimating/estimates/${id}/`);

export const approveEstimate = (id: string) =>
  apiClient.post<Estimate>(`/api/v1/estimating/estimates/${id}/approve/`).then((r) => r.data);

export const copyEstimate = (id: string) =>
  apiClient.post<Estimate>(`/api/v1/estimating/estimates/${id}/copy/`).then((r) => r.data);

export const generateProposal = (estimateId: string, payload: Record<string, unknown>) =>
  apiClient.post<Proposal>(`/api/v1/estimating/estimates/${estimateId}/generate-proposal/`, payload).then((r) => r.data);

export async function fetchProposals(params: Record<string, string> = {}): Promise<ListResponse<Proposal>> {
  const { data } = await apiClient.get<ListResponse<Proposal>>('/api/v1/estimating/proposals/', { params });
  return data;
}

export const updateProposal = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Proposal>(`/api/v1/estimating/proposals/${id}/`, payload).then((r) => r.data);

export const deleteProposal = (id: string) =>
  apiClient.delete(`/api/v1/estimating/proposals/${id}/`);

export async function sendProposal(id: string, email?: string): Promise<Proposal> {
  const { data } = await apiClient.post<Proposal>(`/api/v1/estimating/proposals/${id}/send/`, {
    recipient_email: email,
  });
  return data;
}

export async function fetchCostItems(params: Record<string, string> = {}): Promise<ListResponse<CostItem>> {
  const { data } = await apiClient.get<ListResponse<CostItem>>('/api/v1/estimating/cost-items/', { params });
  return data;
}
