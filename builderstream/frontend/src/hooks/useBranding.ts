import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchBranding, updateBranding, uploadBrandingLogo, BrandingUpdate } from '@/api/branding';

export function useBranding() {
  return useQuery({
    queryKey: ['branding'],
    queryFn: fetchBranding,
    staleTime: 5 * 60 * 1000,
  });
}

/** Apply branding CSS variables + custom CSS to the document. Call once at the layout level. */
export function useApplyBranding() {
  const { data: branding } = useBranding();

  useEffect(() => {
    if (!branding) return;

    // Apply CSS custom properties to :root
    const root = document.documentElement;
    const vars = branding.css_variables ?? {};
    Object.entries(vars).forEach(([prop, value]) => {
      root.style.setProperty(prop, value);
    });

    // Derive --color-primary-rgb (space-separated R G B) for rgba() usage in CSS
    const primaryHex = (vars['--color-primary'] ?? '#3B82F6').replace('#', '');
    const r = parseInt(primaryHex.substring(0, 2), 16);
    const g = parseInt(primaryHex.substring(2, 4), 16);
    const b = parseInt(primaryHex.substring(4, 6), 16);
    if (!isNaN(r) && !isNaN(g) && !isNaN(b)) {
      root.style.setProperty('--color-primary-rgb', `${r} ${g} ${b}`);
    }

    // Apply font-family globally
    if (vars['--font-family']) {
      document.body.style.fontFamily = vars['--font-family'];
    }

    // Inject / update custom CSS
    const styleId = 'bs-branding-custom-css';
    let styleEl = document.getElementById(styleId) as HTMLStyleElement | null;
    if (!styleEl) {
      styleEl = document.createElement('style');
      styleEl.id = styleId;
      document.head.appendChild(styleEl);
    }
    styleEl.textContent = branding.custom_css ?? '';

    // Update favicon if provided
    if (branding.favicon_url) {
      let link = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
      if (!link) {
        link = document.createElement('link');
        link.rel = 'icon';
        document.head.appendChild(link);
      }
      link.href = branding.favicon_url;
    }
  }, [branding]);
}

export function useUpdateBranding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: BrandingUpdate) => updateBranding(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branding'] }),
  });
}

export function useUploadBrandingFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, type }: { file: File; type: 'logo' | 'favicon' }) =>
      uploadBrandingLogo(file, type),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branding'] }),
  });
}
