/**
 * DesktopLayout — full sidebar, multi-column dashboard.
 * Wraps the existing AppLayout behaviour with the sync status bar.
 */
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { SyncStatusBar } from '@/components/mobile/SyncStatusBar';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { label: 'Dashboard', to: '/dashboard' },
      { label: 'Analytics', to: '/analytics' },
    ],
  },
  {
    label: 'Projects',
    items: [
      { label: 'Projects', to: '/projects' },
      { label: 'Scheduling', to: '/scheduling' },
      { label: 'Documents', to: '/documents' },
    ],
  },
  {
    label: 'Sales',
    items: [
      { label: 'CRM', to: '/crm' },
      { label: 'Estimating', to: '/estimating' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { label: 'Field Ops', to: '/field-ops' },
      { label: 'Quality & Safety', to: '/quality-safety' },
      { label: 'Service', to: '/service' },
    ],
  },
  {
    label: 'Finance & HR',
    items: [
      { label: 'Financials', to: '/financials' },
      { label: 'Payroll', to: '/payroll' },
    ],
  },
];

export const DesktopLayout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      {/* Top nav */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-navy-900 shadow-sm">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500">
              <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21" />
              </svg>
            </div>
            <span className="text-lg font-semibold text-white">BuilderStream</span>
          </div>
          <div className="flex items-center gap-4">
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
        <aside className="w-60 flex-shrink-0 border-r border-slate-200 bg-white overflow-y-auto">
          <nav className="flex flex-col p-4 gap-5">
            {NAV_GROUPS.map((group) => (
              <div key={group.label}>
                <p className="mb-1.5 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                  {group.label}
                </p>
                <div className="flex flex-col gap-0.5">
                  {group.items.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        [
                          'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-amber-50 text-amber-700'
                            : 'text-slate-600 hover:bg-slate-50',
                        ].join(' ')
                      }
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </div>
              </div>
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
