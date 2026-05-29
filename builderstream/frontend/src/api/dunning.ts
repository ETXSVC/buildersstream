import { apiClient } from './client';

export interface DunningRule {
  id: string;
  name: string;
  days_past_due: number;
  action_type: 'email_reminder' | 'suspend_portal' | 'flag_escalation';
  email_subject: string;
  email_body: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DunningEvent {
  id: string;
  invoice: string;
  invoice_number: string;
  rule: string | null;
  rule_name: string | null;
  triggered_at: string;
  action_taken: string;
  success: boolean;
  notes: string;
}

export async function fetchDunningRules(): Promise<{ results: DunningRule[]; count: number }> {
  const { data } = await apiClient.get('/api/v1/financials/dunning-rules/');
  return data;
}

export async function createDunningRule(payload: Partial<DunningRule>): Promise<DunningRule> {
  const { data } = await apiClient.post('/api/v1/financials/dunning-rules/', payload);
  return data;
}

export async function updateDunningRule(id: string, payload: Partial<DunningRule>): Promise<DunningRule> {
  const { data } = await apiClient.patch(`/api/v1/financials/dunning-rules/${id}/`, payload);
  return data;
}

export async function deleteDunningRule(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/financials/dunning-rules/${id}/`);
}

export async function fetchDunningEvents(params?: Record<string, string>): Promise<{ results: DunningEvent[]; count: number }> {
  const { data } = await apiClient.get('/api/v1/financials/dunning-events/', { params });
  return data;
}
