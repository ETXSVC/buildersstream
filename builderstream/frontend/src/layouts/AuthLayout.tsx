import { Outlet } from 'react-router-dom';

export const AuthLayout = () => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-navy-900 to-navy-800 px-4">
      {/* Branding */}
      <div className="mb-8 text-center">
        <div className="mb-2 flex items-center justify-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500">
            <svg
              className="h-6 w-6 text-white"
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
          <h1 className="text-2xl font-bold text-white">BuilderStream</h1>
        </div>
        <p className="text-sm text-navy-300">
          Construction Management Platform
        </p>
      </div>

      {/* Card */}
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-2xl">
        <Outlet />
      </div>

      {/* Footer */}
      <p className="mt-8 text-xs text-navy-400">
        &copy; {new Date().getFullYear()} BuilderStream. All rights reserved.
      </p>
    </div>
  );
};
