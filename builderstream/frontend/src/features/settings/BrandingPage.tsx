import { useState, useRef } from 'react';
import { useBranding, useUpdateBranding, useUploadBrandingFile } from '@/hooks/useBranding';
import { SubNav } from '@/components/SubNav';
const SUBNAV = [{ label: 'Branding', to: '/settings/branding' }, { label: 'Dunning', to: '/settings/dunning' }, { label: 'Custom Fields', to: '/settings/custom-fields' }];

const DEFAULT_COLORS = {
  primary_color: '#3B82F6',
  primary_dark: '#2563EB',
  accent_color: '#1e293b',
  sidebar_bg: '#0f172a',
  sidebar_text: '#f8fafc',
};

export const BrandingPage = () => {
  const { data: branding, isLoading } = useBranding();
  const update = useUpdateBranding();
  const upload = useUploadBrandingFile();
  const logoInputRef = useRef<HTMLInputElement>(null);
  const faviconInputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({
    company_name_override: '',
    primary_color: DEFAULT_COLORS.primary_color,
    primary_dark: DEFAULT_COLORS.primary_dark,
    accent_color: DEFAULT_COLORS.accent_color,
    sidebar_bg: DEFAULT_COLORS.sidebar_bg,
    sidebar_text: DEFAULT_COLORS.sidebar_text,
    font_family: 'Inter, sans-serif',
    support_email: '',
    support_phone: '',
    portal_welcome_message: '',
    custom_css: '',
  });
  const [initialized, setInitialized] = useState(false);
  const [saved, setSaved] = useState(false);

  if (branding && !initialized) {
    const cv = branding.css_variables ?? {};
    setForm({
      company_name_override: branding.company_name ?? '',
      primary_color: cv['--color-primary'] ?? DEFAULT_COLORS.primary_color,
      primary_dark: cv['--color-primary-dark'] ?? DEFAULT_COLORS.primary_dark,
      accent_color: cv['--color-accent'] ?? DEFAULT_COLORS.accent_color,
      sidebar_bg: cv['--color-sidebar-bg'] ?? DEFAULT_COLORS.sidebar_bg,
      sidebar_text: cv['--color-sidebar-text'] ?? DEFAULT_COLORS.sidebar_text,
      font_family: cv['--font-family'] ?? 'Inter, sans-serif',
      support_email: branding.support_email ?? '',
      support_phone: branding.support_phone ?? '',
      portal_welcome_message: branding.portal_welcome_message ?? '',
      custom_css: branding.custom_css ?? '',
    });
    setInitialized(true);
  }

  const handleSave = async () => {
    await update.mutateAsync(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleFileChange = (type: 'logo' | 'favicon') => (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) upload.mutate({ file, type });
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl space-y-8">
      <SubNav items={SUBNAV} />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Branding</h1>
          <p className="text-sm text-slate-500 mt-1">Customize your organization's appearance</p>
        </div>
        <button
          type="button"
          onClick={handleSave}
          disabled={update.isPending}
          className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-60"
        >
          {update.isPending ? 'Saving…' : saved ? 'Saved!' : 'Save Changes'}
        </button>
      </div>

      {/* Logo & Favicon */}
      <Section title="Logos">
        <div className="flex flex-wrap gap-8">
          <LogoUpload
            label="Company Logo"
            url={branding?.logo_url ?? null}
            description="PNG or SVG recommended. Shown in navigation."
            inputRef={logoInputRef}
            onUpload={() => logoInputRef.current?.click()}
            onChange={handleFileChange('logo')}
            loading={upload.isPending}
          />
          <LogoUpload
            label="Favicon"
            url={branding?.favicon_url ?? null}
            description="32×32 ICO or PNG for browser tabs."
            inputRef={faviconInputRef}
            onUpload={() => faviconInputRef.current?.click()}
            onChange={handleFileChange('favicon')}
            loading={upload.isPending}
          />
        </div>
      </Section>

      {/* Company Name */}
      <Section title="Company Name">
        <FormField label="Override Display Name" hint="Replaces your organization name in the UI and portal.">
          <input
            type="text"
            value={form.company_name_override}
            onChange={(e) => setForm((f) => ({ ...f, company_name_override: e.target.value }))}
            placeholder={branding?.company_name ?? 'Your Company'}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
          />
        </FormField>
      </Section>

      {/* Colors */}
      <Section title="Colors">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <ColorField label="Primary" value={form.primary_color} onChange={(v) => setForm((f) => ({ ...f, primary_color: v }))} />
          <ColorField label="Primary Dark" value={form.primary_dark} onChange={(v) => setForm((f) => ({ ...f, primary_dark: v }))} />
          <ColorField label="Accent" value={form.accent_color} onChange={(v) => setForm((f) => ({ ...f, accent_color: v }))} />
          <ColorField label="Sidebar Background" value={form.sidebar_bg} onChange={(v) => setForm((f) => ({ ...f, sidebar_bg: v }))} />
          <ColorField label="Sidebar Text" value={form.sidebar_text} onChange={(v) => setForm((f) => ({ ...f, sidebar_text: v }))} />
        </div>
        <div className="mt-3">
          <ColorPreview colors={form} />
        </div>
      </Section>

      {/* Font */}
      <Section title="Typography">
        <FormField label="Font Family" hint="CSS font-family value applied globally.">
          <select
            value={form.font_family}
            onChange={(e) => setForm((f) => ({ ...f, font_family: e.target.value }))}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
          >
            <option value="Inter, sans-serif">Inter (default)</option>
            <option value="Roboto, sans-serif">Roboto</option>
            <option value="'Open Sans', sans-serif">Open Sans</option>
            <option value="'DM Sans', sans-serif">DM Sans</option>
            <option value="Georgia, serif">Georgia</option>
          </select>
        </FormField>
      </Section>

      {/* Client Portal */}
      <Section title="Client Portal">
        <div className="grid gap-4">
          <FormField label="Support Email">
            <input
              type="email"
              value={form.support_email}
              onChange={(e) => setForm((f) => ({ ...f, support_email: e.target.value }))}
              placeholder="support@yourcompany.com"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
            />
          </FormField>
          <FormField label="Support Phone">
            <input
              type="tel"
              value={form.support_phone}
              onChange={(e) => setForm((f) => ({ ...f, support_phone: e.target.value }))}
              placeholder="+1 (555) 000-0000"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
            />
          </FormField>
          <FormField label="Portal Welcome Message" hint="Shown on the client portal login screen.">
            <textarea
              rows={3}
              value={form.portal_welcome_message}
              onChange={(e) => setForm((f) => ({ ...f, portal_welcome_message: e.target.value }))}
              placeholder="Welcome to our client portal…"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
            />
          </FormField>
        </div>
      </Section>

      {/* Custom CSS */}
      <Section title="Custom CSS">
        <FormField label="Additional CSS" hint="Injected into every page. Use with caution.">
          <textarea
            rows={6}
            value={form.custom_css}
            onChange={(e) => setForm((f) => ({ ...f, custom_css: e.target.value }))}
            placeholder="/* .my-class { color: red; } */"
            className="w-full rounded-lg border border-slate-200 px-3 py-2 font-mono text-xs focus:border-blue-400 focus:outline-none"
          />
        </FormField>
      </Section>
    </div>
  );
};

/* ---------- Sub-components ---------- */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
      <h2 className="text-sm font-semibold text-slate-700">{title}</h2>
      {children}
    </div>
  );
}

function FormField({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      {children}
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  );
}

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-8 w-10 cursor-pointer rounded border border-slate-200 p-0.5"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 rounded-lg border border-slate-200 px-2 py-1.5 font-mono text-xs focus:border-blue-400 focus:outline-none"
        />
      </div>
    </div>
  );
}

function ColorPreview({ colors }: { colors: typeof DEFAULT_COLORS & { sidebar_text: string } }) {
  return (
    <div className="flex items-center gap-2 rounded-lg overflow-hidden border border-slate-200 text-xs">
      <div
        className="flex flex-col items-center justify-center px-4 py-3 min-w-[100px] text-white"
        style={{ backgroundColor: colors.sidebar_bg, color: colors.sidebar_text }}
      >
        <div className="w-3 h-3 rounded-full mb-1" style={{ backgroundColor: colors.primary_color }} />
        <span>Sidebar</span>
      </div>
      <div className="flex-1 py-3 px-4 bg-white">
        <div
          className="inline-flex items-center rounded px-3 py-1 text-white text-xs font-medium"
          style={{ backgroundColor: colors.primary_color }}
        >
          Primary Button
        </div>
      </div>
    </div>
  );
}

function LogoUpload({
  label, url, description, inputRef, onUpload, onChange, loading,
}: {
  label: string;
  url: string | null;
  description: string;
  inputRef: React.RefObject<HTMLInputElement>;
  onUpload: () => void;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  loading: boolean;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-medium text-slate-600">{label}</label>
      <div className="flex h-20 w-32 items-center justify-center rounded-lg border-2 border-dashed border-slate-200 bg-slate-50">
        {url ? (
          <img src={url} alt={label} className="max-h-16 max-w-28 object-contain" />
        ) : (
          <span className="text-xs text-slate-400">No image</span>
        )}
      </div>
      <button
        type="button"
        onClick={onUpload}
        disabled={loading}
        className="text-xs text-blue-600 hover:underline disabled:opacity-50"
      >
        {loading ? 'Uploading…' : 'Upload'}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onChange}
      />
      <p className="text-xs text-slate-400">{description}</p>
    </div>
  );
}
