/**
 * TabletLayout — collapsible sidebar, two-column where appropriate.
 */
import { useState } from 'react';
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

export const TabletLayout = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      {/* Top bar */}
      <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-slate-200 bg-white px-4 shadow-sm">
        <button
          type="button"
          onClick={() => setSidebarOpen((o) => !o)}
          aria-label="Toggle sidebar"
          className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="flex-1 text-sm font-semibold text-slate-900">BuilderStream</span>
        <span className="text-sm text-slate-500">{user?.first_name}</span>
        <button type="button" onClick={logout}
          className="rounded-md px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100">
          Sign out
        </button>
      </header>

      <SyncStatusBar />

      <div className="flex flex-1 overflow-hidden">
        {/* Collapsible sidebar */}
        {sidebarOpen && (
          <aside className="w-56 flex-shrink-0 border-r border-slate-200 bg-white overflow-y-auto">
            <nav className="flex flex-col p-3 gap-4">
              {NAV_GROUPS.map((group) => (
                <div key={group.label}>
                  <p className="mb-1 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {group.label}
                  </p>
                  <div className="flex flex-col gap-0.5">
                    {group.items.map((item) => (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        onClick={() => setSidebarOpen(false)}
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
        )}

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
