import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchContacts,
  fetchLeads,
  fetchPipelineStages,
  createContact,
  updateContact,
  deleteContact,
  createLead,
  updateLead,
  deleteLead,
} from '@/api/crm';
import type { Contact, Lead } from '@/types/crm';

// ── Contacts ──────────────────────────────────────────────────────────────────

export function useContacts(search?: string, page = 1) {
  return useQuery({
    queryKey: ['crm', 'contacts', { search, page }],
    queryFn: () => fetchContacts(search, page),
    staleTime: 30 * 1000,
  });
}

export function useCreateContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<Contact>) => createContact(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'contacts'] }),
  });
}

export function useUpdateContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<Contact> }) =>
      updateContact(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'contacts'] }),
  });
}

export function useDeleteContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteContact(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'contacts'] }),
  });
}

// ── Leads ─────────────────────────────────────────────────────────────────────

export function useLeads(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ['crm', 'leads', params],
    queryFn: () => fetchLeads(params),
    staleTime: 30 * 1000,
  });
}

export function useCreateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<Lead>) => createLead(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'leads'] }),
  });
}

export function useUpdateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<Lead> }) =>
      updateLead(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'leads'] }),
  });
}

export function useDeleteLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteLead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['crm', 'leads'] }),
  });
}

// ── Pipeline Stages ────────────────────────────────────────────────────────────

export function usePipelineStages() {
  return useQuery({
    queryKey: ['crm', 'pipeline-stages'],
    queryFn: fetchPipelineStages,
    staleTime: 5 * 60 * 1000,
  });
}
