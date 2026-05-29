import { apiClient } from './client';

export interface BrandingData {
  company_name: string;
  logo_url: string | null;
  favicon_url: string | null;
  css_variables: Record<string, string>;
  custom_css: string;
  support_email: string;
  support_phone: string;
  portal_welcome_message: string;
}

export interface BrandingUpdate {
  company_name_override?: string;
  primary_color?: string;
  primary_dark?: string;
  accent_color?: string;
  sidebar_bg?: string;
  sidebar_text?: string;
  font_family?: string;
  custom_css?: string;
  support_email?: string;
  support_phone?: string;
  portal_welcome_message?: string;
}

export async function fetchBranding(): Promise<BrandingData> {
  const { data } = await apiClient.get('/api/v1/tenants/branding/');
  return data;
}

export async function updateBranding(payload: BrandingUpdate): Promise<{ detail: string }> {
  const { data } = await apiClient.put('/api/v1/tenants/branding/', payload);
  return data;
}

export async function uploadBrandingLogo(file: File, type: 'logo' | 'favicon'): Promise<{ detail: string }> {
  const form = new FormData();
  form.append(type, file);
  const { data } = await apiClient.put('/api/v1/tenants/branding/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
