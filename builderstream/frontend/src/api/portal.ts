/**
 * Client Portal API — uses "Authorization: Portal <token>" scheme.
 * Completely separate from the main contractor API client.
 */
import axios from 'axios';

const PORTAL_TOKEN_KEY = 'portal_jwt';

export function getPortalToken(): string | null {
  return localStorage.getItem(PORTAL_TOKEN_KEY);
}

export function setPortalToken(token: string) {
  localStorage.setItem(PORTAL_TOKEN_KEY, token);
}

export function clearPortalToken() {
  localStorage.removeItem(PORTAL_TOKEN_KEY);
}

export const portalClient = axios.create({ baseURL: '/' });

portalClient.interceptors.request.use((config) => {
  const token = getPortalToken();
  if (token) config.headers.Authorization = `Portal ${token}`;
  return config;
});

// ─── Types ───────────────────────────────────────────────────────────────────

export interface PortalBranding {
  company_name: string;
  primary_color: string | null;
  logo_url: string | null;
  welcome_message: string | null;
}

export interface PortalProject {
  id: string;
  name: string;
  project_number: string;
  status: string;
  percent_complete: number;
  start_date: string | null;
  estimated_completion: string | null;
  actual_completion: string | null;
  address: string | null;
}

export interface PortalDashboard {
  project: PortalProject;
  pending_selections: number;
  pending_approvals: number;
  unread_messages: number;
  branding: PortalBranding | null;
}

export interface PortalSelectionOption {
  id: string;
  name: string;
  description: string;
  price: string | null;
  price_difference: string | null;
  lead_time_days: number | null;
  supplier: string;
  spec_sheet_url: string | null;
  image_url: string | null;
  is_recommended: boolean;
}

export interface PortalSelection {
  id: string;
  name: string;
  category: string;
  status: string;
  due_date: string | null;
  notes: string;
  options: PortalSelectionOption[];
  selected_option: string | null;
}

export interface PortalApproval {
  id: string;
  title: string;
  approval_type: string;
  status: string;
  description: string;
  amount: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface PortalMessage {
  id: string;
  sender_type: 'contractor' | 'client';
  sender_name: string | null;
  subject: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export interface PortalMilestone {
  id: string;
  name: string;
  due_date: string | null;
  is_complete: boolean;
  completed_at: string | null;
}

export interface PortalSchedule {
  project: PortalProject;
  milestones: PortalMilestone[];
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export async function portalLogin(access_token: string, pin_code?: string): Promise<string> {
  const { data } = await portalClient.post<{ token: string }>('/api/v1/portal/login/', {
    access_token,
    ...(pin_code ? { pin_code } : {}),
  });
  return data.token;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export async function fetchPortalDashboard(): Promise<PortalDashboard> {
  const { data } = await portalClient.get<PortalDashboard>('/api/v1/portal/dashboard/');
  return data;
}

// ─── Selections ──────────────────────────────────────────────────────────────

export async function fetchPortalSelections(): Promise<PortalSelection[]> {
  const { data } = await portalClient.get<PortalSelection[] | { results: PortalSelection[] }>('/api/v1/portal/selections/');
  return Array.isArray(data) ? data : data.results;
}

export async function fetchPortalSelection(id: string): Promise<PortalSelection> {
  const { data } = await portalClient.get<PortalSelection>(`/api/v1/portal/selections/${id}/`);
  return data;
}

export async function submitSelectionChoice(id: string, selection_option: string, notes?: string) {
  await portalClient.post(`/api/v1/portal/selections/${id}/choose/`, { selection_option, notes: notes ?? '' });
}

// ─── Approvals ───────────────────────────────────────────────────────────────

export async function fetchPortalApprovals(): Promise<PortalApproval[]> {
  const { data } = await portalClient.get<PortalApproval[] | { results: PortalApproval[] }>('/api/v1/portal/approvals/');
  return Array.isArray(data) ? data : data.results;
}

export async function fetchPortalApproval(id: string): Promise<PortalApproval> {
  const { data } = await portalClient.get<PortalApproval>(`/api/v1/portal/approvals/${id}/`);
  return data;
}

export async function respondToApproval(id: string, approved: boolean, response_notes?: string) {
  await portalClient.post(`/api/v1/portal/approvals/${id}/respond/`, {
    approved,
    response_notes: response_notes ?? '',
  });
}

// ─── Messages ────────────────────────────────────────────────────────────────

export async function fetchPortalMessages(): Promise<PortalMessage[]> {
  const { data } = await portalClient.get<PortalMessage[] | { results: PortalMessage[] }>('/api/v1/portal/messages/');
  return Array.isArray(data) ? data : data.results;
}

export async function sendPortalMessage(subject: string, body: string) {
  await portalClient.post('/api/v1/portal/messages/', { subject, body });
}

// ─── Schedule ────────────────────────────────────────────────────────────────

export async function fetchPortalSchedule(): Promise<PortalSchedule> {
  const { data } = await portalClient.get<PortalSchedule>('/api/v1/portal/schedule/');
  return data;
}

// ─── Survey ──────────────────────────────────────────────────────────────────

export async function submitPortalSurvey(rating: number, nps_score: number, feedback: string) {
  await portalClient.post('/api/v1/portal/survey/', { rating, nps_score, feedback });
}
