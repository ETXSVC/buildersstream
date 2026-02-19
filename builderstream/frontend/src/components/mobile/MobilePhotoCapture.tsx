/**
 * MobilePhotoCapture — camera integration for field photo capture.
 * Auto-tags with current project. Queues photos for upload when offline.
 */
import { useRef, useState } from 'react';
import { offlineDb } from '@/services/offlineDb';

type Props = {
  projectId?: string;
  albumId?: string;
  onCapture?: (photoId: string) => void;
};

export const MobilePhotoCapture = ({ projectId = '', albumId, onCapture }: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'idle' | 'queued' | 'error'>('idle');

  const handleCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
  };

  const handleQueue = async () => {
    if (!fileInputRef.current?.files?.[0]) return;
    const file = fileInputRef.current.files[0];

    try {
      const id = `photo_${Date.now()}_${Math.random().toString(36).slice(2)}`;
      await offlineDb.queuePhoto({
        id,
        projectId,
        albumId,
        blob: file,
        description: description.trim() || undefined,
        queuedAt: new Date().toISOString(),
      });
      setStatus('queued');
      onCapture?.(id);
      setPreview(null);
      setDescription('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch {
      setStatus('error');
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <h2 className="text-lg font-semibold text-slate-900">Capture Photo</h2>

      {/* Camera trigger */}
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="flex h-48 w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 text-slate-500 hover:border-amber-400 hover:bg-amber-50 hover:text-amber-600 transition-colors"
      >
        {preview ? (
          <img src={preview} alt="Preview" className="h-full w-full rounded-xl object-cover" />
        ) : (
          <>
            <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-sm font-medium">Tap to open camera</span>
          </>
        )}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleCapture}
        aria-label="Camera input"
      />

      {preview && (
        <>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add a description (optional)"
            className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-200"
          />

          <button
            type="button"
            onClick={handleQueue}
            className="w-full rounded-xl bg-amber-500 py-3 text-base font-semibold text-white hover:bg-amber-600"
          >
            {navigator.onLine ? 'Upload Photo' : 'Queue for Upload'}
          </button>
        </>
      )}

      {status === 'queued' && (
        <p className="text-center text-sm text-green-600">Photo queued — will upload when online.</p>
      )}
      {status === 'error' && (
        <p className="text-center text-sm text-red-600">Failed to queue photo. Try again.</p>
      )}
    </div>
  );
};
