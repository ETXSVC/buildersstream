import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, Download } from 'lucide-react';
import { portalClient } from '@/api/portal';

interface PortalPhoto {
  id: string;
  caption: string | null;
  thumbnail_url: string | null;
  download_url: string | null;
  taken_at: string | null;
  category: string;
  phase: string;
  created_at: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  PROGRESS: 'Progress',
  BEFORE: 'Before',
  AFTER: 'After',
  DEFICIENCY: 'Deficiency',
  DELIVERY: 'Delivery',
  INSPECTION: 'Inspection',
  SAFETY: 'Safety',
  OTHER: 'Other',
};

async function fetchPortalPhotos(): Promise<PortalPhoto[]> {
  const { data } = await portalClient.get<{ results: PortalPhoto[] }>('/api/v1/portal/photos/');
  return data.results;
}

export function PortalPhotos() {
  const [lightbox, setLightbox] = useState<PortalPhoto | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('all');

  const { data = [], isLoading, error } = useQuery({
    queryKey: ['portal', 'photos'],
    queryFn: fetchPortalPhotos,
    staleTime: 60_000,
  });

  const categories = ['all', ...Array.from(new Set(data.map((p) => p.category)))];
  const filtered = activeCategory === 'all' ? data : data.filter((p) => p.category === activeCategory);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-slate-900">Project Photos</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load photos.
        </div>
      )}

      {!isLoading && !error && (
        <>
          {/* Category filter */}
          {categories.length > 2 && (
            <div className="flex gap-2 flex-wrap">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                    activeCategory === cat
                      ? 'bg-amber-500 text-white'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {cat === 'all' ? `All (${data.length})` : `${CATEGORY_LABELS[cat] ?? cat} (${data.filter((p) => p.category === cat).length})`}
                </button>
              ))}
            </div>
          )}

          {filtered.length === 0 ? (
            <div className="rounded-2xl bg-white border border-slate-200 p-10 text-center text-slate-400 text-sm">
              No photos yet.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
              {filtered.map((photo) => (
                <button
                  key={photo.id}
                  type="button"
                  onClick={() => setLightbox(photo)}
                  className="group relative aspect-square rounded-xl overflow-hidden bg-slate-100"
                >
                  {photo.thumbnail_url ? (
                    <img
                      src={photo.thumbnail_url}
                      alt={photo.caption ?? ''}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-300 text-xs">No preview</div>
                  )}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
                  {photo.caption && (
                    <div className="absolute bottom-0 left-0 right-0 px-2 py-1 bg-black/50 text-white text-xs truncate opacity-0 group-hover:opacity-100 transition-opacity">
                      {photo.caption}
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </>
      )}

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setLightbox(null)}
        >
          <div className="relative max-w-3xl w-full" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              onClick={() => setLightbox(null)}
              className="absolute -top-10 right-0 text-white hover:text-amber-400"
            >
              <X size={24} />
            </button>

            {lightbox.download_url ? (
              <img
                src={lightbox.download_url}
                alt={lightbox.caption ?? ''}
                className="w-full rounded-xl max-h-[75vh] object-contain"
              />
            ) : lightbox.thumbnail_url ? (
              <img
                src={lightbox.thumbnail_url}
                alt={lightbox.caption ?? ''}
                className="w-full rounded-xl max-h-[75vh] object-contain"
              />
            ) : null}

            <div className="mt-3 flex items-center justify-between px-1">
              <div>
                {lightbox.caption && <p className="text-white text-sm">{lightbox.caption}</p>}
                <p className="text-slate-400 text-xs mt-0.5">
                  {CATEGORY_LABELS[lightbox.category] ?? lightbox.category}
                  {lightbox.taken_at && ` · ${new Date(lightbox.taken_at).toLocaleDateString()}`}
                </p>
              </div>
              {lightbox.download_url && (
                <a
                  href={lightbox.download_url}
                  download
                  className="flex items-center gap-1.5 text-xs text-amber-400 hover:text-amber-300 font-medium"
                >
                  <Download size={13} /> Download
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
