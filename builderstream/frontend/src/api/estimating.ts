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

export async function fetchProposals(params: Record<string, string> = {}): Promise<ListResponse<Proposal>> {
  const { data } = await apiClient.get<ListResponse<Proposal>>('/api/v1/estimating/proposals/', { params });
  return data;
}

export async function fetchCostItems(params: Record<string, string> = {}): Promise<ListResponse<CostItem>> {
  const { data } = await apiClient.get<ListResponse<CostItem>>('/api/v1/estimating/cost-items/', { params });
  return data;
}

export async function sendProposal(id: string, email?: string): Promise<Proposal> {
  const { data } = await apiClient.post<Proposal>(`/api/v1/estimating/proposals/${id}/send/`, {
    recipient_email: email,
  });
  return data;
}
