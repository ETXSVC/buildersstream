import { useEffect, useState } from 'react';
import { X, Zap } from 'lucide-react';
import type { UpgradeRequiredPayload } from '@/api/client';

/**
 * Global modal that fires when any API call returns 402 with upgrade_required:true.
 * Mounted once in App.tsx; listens to the 'upgrade-required' custom window event.
 */
export function UpgradeModal() {
  const [payload, setPayload] = useState<UpgradeRequiredPayload | null>(null);

  useEffect(() => {
    function handler(e: Event) {
      setPayload((e as CustomEvent<UpgradeRequiredPayload>).detail);
    }
    window.addEventListener('upgrade-required', handler);
    return () => window.removeEventListener('upgrade-required', handler);
  }, []);

  if (!payload) return null;

  const pct = payload.limit > 0 ? Math.min((payload.current / payload.limit) * 100, 100) : 100;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-8">
        <button
          onClick={() => setPayload(null)}
          className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Icon */}
        <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600/20 border border-blue-500/30 mb-6">
          <Zap className="h-7 w-7 text-blue-400" />
        </div>

        <h2 className="text-xl font-bold text-white mb-2">Plan Limit Reached</h2>
        <p className="text-slate-400 text-sm mb-6 leading-relaxed">{payload.detail}</p>

        {/* Usage bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-500 mb-1.5">
            <span>Usage</span>
            <span>{payload.current} / {payload.limit}</span>
          </div>
          <div className="h-2 rounded-full bg-slate-700 overflow-hidden">
            <div
              className="h-full rounded-full bg-blue-500 transition-all"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <a
            href="/settings/billing"
            className="w-full text-center bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-xl transition-colors text-sm"
            onClick={() => setPayload(null)}
          >
            Upgrade Plan
          </a>
          <button
            onClick={() => setPayload(null)}
            className="w-full text-center border border-slate-700 hover:border-slate-500 text-slate-400 hover:text-white font-semibold py-3 rounded-xl transition-colors text-sm"
          >
            Maybe Later
          </button>
        </div>
      </div>
    </div>
  );
}
