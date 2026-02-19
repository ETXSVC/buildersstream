import { apiClient } from '@/api/client';
import type { Contact, ContactListResponse, Lead, LeadListResponse, PipelineStage } from '@/types/crm';

export async function fetchContacts(search?: string, page = 1): Promise<ContactListResponse> {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set('search', search);
  const { data } = await apiClient.get<ContactListResponse>('/api/v1/crm/contacts/', { params });
  return data;
}

export async function fetchLeads(params: Record<string, string> = {}): Promise<LeadListResponse> {
  const { data } = await apiClient.get<LeadListResponse>('/api/v1/crm/leads/', { params });
  return data;
}

export async function fetchPipelineStages(): Promise<PipelineStage[]> {
  const { data } = await apiClient.get<{ results: PipelineStage[] }>('/api/v1/crm/pipeline-stages/');
  return data.results;
}

export async function fetchContact(id: string): Promise<Contact> {
  const { data } = await apiClient.get<Contact>(`/api/v1/crm/contacts/${id}/`);
  return data;
}

export async function fetchLead(id: string): Promise<Lead> {
  const { data } = await apiClient.get<Lead>(`/api/v1/crm/leads/${id}/`);
  return data;
}
