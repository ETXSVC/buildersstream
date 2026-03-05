import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchBranding, updateBranding, uploadBrandingLogo, BrandingUpdate } from '@/api/branding';

export function useBranding() {
  return useQuery({
    queryKey: ['branding'],
    queryFn: fetchBranding,
    staleTime: 5 * 60 * 1000,
  });
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
