/**
 * MobileLayout — no sidebar, stacked cards, bottom nav, safe-area padding.
 */
import { Outlet } from 'react-router-dom';
import { MobileNavigation } from '@/components/mobile/MobileNavigation';
import { SyncStatusBar } from '@/components/mobile/SyncStatusBar';
import { useAuth } from '@/hooks/useAuth';

export const MobileLayout = () => {
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      {/* Minimal top bar */}
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-amber-500">
            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-900">BuilderStream</span>
        </div>
        <button
          type="button"
          onClick={logout}
          aria-label="Sign out"
          className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </header>

      <SyncStatusBar />

      {/* Scrollable content, padded above bottom nav */}
      <main className="flex-1 overflow-y-auto pb-20">
        <Outlet />
      </main>

      <MobileNavigation />
    </div>
  );
};
