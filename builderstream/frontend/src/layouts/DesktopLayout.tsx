/**
 * DesktopLayout — full sidebar, multi-column dashboard.
 * Wraps the existing AppLayout behaviour with the sync status bar.
 */
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useBranding } from '@/hooks/useBranding';
import { SyncStatusBar } from '@/components/mobile/SyncStatusBar';
import { NotificationBell } from '@/components/NotificationBell';
import { CommandPalette } from '@/components/CommandPalette';

const NAV_ITEMS = [
  { label: 'Overview',     to: '/dashboard' },
  { label: 'Projects',     to: '/projects' },
  { label: 'Sales',        to: '/crm' },
  { label: 'Operations',   to: '/field-ops' },
  { label: 'Finance & HR', to: '/financials' },
  { label: 'Company',      to: '/company' },
  { label: 'Team Messaging', to: '/collaboration' },
  { label: 'Settings',     to: '/settings/branding' },
];

const buildTime = (window as unknown as { __BUILD_TIME__?: string }).__BUILD_TIME__ ?? '';

export const DesktopLayout = () => {
  const { user, logout } = useAuth();
  const { data: branding } = useBranding();
  const siteName = branding?.company_name || 'BuilderStream';
  const logoUrl = branding?.logo_url ?? null;

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <CommandPalette />
      {/* Top nav */}
      <header className="bs-sidebar sticky top-0 z-40 border-b border-slate-700 shadow-sm">
        <div className="grid h-16 grid-cols-3 items-center px-6">
          {/* Left: Logo + site name */}
          <div className="flex items-center gap-3">
            {logoUrl ? (
              <img src={logoUrl} alt={siteName} className="h-8 w-8 rounded-lg object-contain" />
            ) : (
              <div className="bs-primary-icon flex h-8 w-8 items-center justify-center rounded-lg">
                <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round"
                    d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21" />
                </svg>
              </div>
            )}
            <span className="text-lg font-semibold">{siteName}</span>
          </div>

          {/* Center: Build timestamp */}
          <div className="flex justify-center">
            {buildTime && (
              <span className="rounded bg-slate-700/60 px-2 py-0.5 font-mono text-[10px] text-slate-400">
                Build: {new Date(buildTime).toLocaleString()}
              </span>
            )}
          </div>

          {/* Right: actions */}
          <div className="flex items-center justify-end gap-3">
            {/* Search shortcut button */}
            <button
              type="button"
              onClick={() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }))}
              className="hidden md:flex items-center gap-2 rounded-lg border border-slate-600 bg-slate-700/50 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-700 hover:text-white"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              Search
              <kbd className="rounded bg-slate-600 px-1">⌘K</kbd>
            </button>
            <NotificationBell />
            <span className="text-sm text-slate-300">{user?.first_name} {user?.last_name}</span>
            <button type="button" onClick={logout}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700 hover:text-white">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <SyncStatusBar />

      <div className="flex flex-1 overflow-hidden">
        {/* Full sidebar */}
        <aside className="w-52 flex-shrink-0 border-r border-slate-200 bg-white overflow-y-auto">
          <nav className="flex flex-col p-3 gap-0.5 pt-4">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    'rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bs-sidebar-link-active'
                      : 'text-slate-600 hover:bg-slate-50',
                  ].join(' ')
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
