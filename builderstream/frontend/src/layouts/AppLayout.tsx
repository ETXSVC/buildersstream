import { Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export const AppLayout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top nav */}
      <header className="border-b border-slate-200 bg-navy-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 0-.75 3.75m0 0-.75 3.75M17.25 7.5l.75 3.75m0 0 .75 3.75"
                />
              </svg>
            </div>
            <span className="text-lg font-semibold text-white">
              BuilderStream
            </span>
          </div>

          {/* User menu */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-navy-200">
              {user?.first_name} {user?.last_name}
            </span>
            <button
              onClick={logout}
              className="min-h-11 rounded-lg border border-navy-600 px-4 py-2 text-sm font-medium text-navy-200 transition-colors hover:bg-navy-800 hover:text-white"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
};
