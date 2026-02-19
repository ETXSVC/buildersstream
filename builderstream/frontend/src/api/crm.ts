import { apiClient } from '@/api/client';
import type { Contact, ContactListResponse, Lead, LeadListResponse, PipelineStage } from '@/types/crm';

// ── Contacts ──────────────────────────────────────────────────────────────────

export async function fetchContacts(search?: string, page = 1): Promise<ContactListResponse> {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set('search', search);
  const { data } = await apiClient.get<ContactListResponse>('/api/v1/crm/contacts/', { params });
  return data;
}

export async function fetchContact(id: string): Promise<Contact> {
  const { data } = await apiClient.get<Contact>(`/api/v1/crm/contacts/${id}/`);
  return data;
}

export async function createContact(payload: Partial<Contact>): Promise<Contact> {
  const { data } = await apiClient.post<Contact>('/api/v1/crm/contacts/', payload);
  return data;
}

export async function updateContact(id: string, payload: Partial<Contact>): Promise<Contact> {
  const { data } = await apiClient.patch<Contact>(`/api/v1/crm/contacts/${id}/`, payload);
  return data;
}

export async function deleteContact(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/crm/contacts/${id}/`);
}

// ── Leads ─────────────────────────────────────────────────────────────────────

export async function fetchLeads(params: Record<string, string> = {}): Promise<LeadListResponse> {
  const { data } = await apiClient.get<LeadListResponse>('/api/v1/crm/leads/', { params });
  return data;
}

export async function fetchLead(id: string): Promise<Lead> {
  const { data } = await apiClient.get<Lead>(`/api/v1/crm/leads/${id}/`);
  return data;
}

export async function createLead(payload: Partial<Lead>): Promise<Lead> {
  const { data } = await apiClient.post<Lead>('/api/v1/crm/leads/', payload);
  return data;
}

export async function updateLead(id: string, payload: Partial<Lead>): Promise<Lead> {
  const { data } = await apiClient.patch<Lead>(`/api/v1/crm/leads/${id}/`, payload);
  return data;
}

export async function deleteLead(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/crm/leads/${id}/`);
}

// ── Pipeline Stages ────────────────────────────────────────────────────────────

export async function fetchPipelineStages(): Promise<PipelineStage[]> {
  const { data } = await apiClient.get<{ results: PipelineStage[] }>('/api/v1/crm/pipeline-stages/');
  return data.results;
}
