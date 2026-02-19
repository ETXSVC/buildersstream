import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ResponsiveLayout } from '@/layouts/ResponsiveLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoginPage } from '@/features/auth';
import { DashboardPage } from '@/features/dashboard';
import { ProjectsPage, ProjectDetailPage } from '@/features/projects';
import { ClockPage, DailyLogPage, CameraPage, FieldOpsPage } from '@/features/field-ops';
import { CRMPage } from '@/features/crm';

export const router = createBrowserRouter(
  [
    {
      // Unauthenticated routes
      element: <AuthLayout />,
      children: [
        { path: '/login', element: <LoginPage /> },
        {
          path: '/register',
          element: (
            <div className="py-8 text-center text-slate-500">
              Registration page coming soon.
            </div>
          ),
        },
        {
          path: '/forgot-password',
          element: (
            <div className="py-8 text-center text-slate-500">
              Password reset page coming soon.
            </div>
          ),
        },
      ],
    },
    {
      // Authenticated routes
      element: <ProtectedRoute />,
      children: [
        {
          element: <ResponsiveLayout />,
          children: [
            { path: '/', element: <Navigate to="/dashboard" replace /> },
            { path: '/dashboard', element: <DashboardPage /> },

            // Projects
            { path: '/projects', element: <ProjectsPage /> },
            { path: '/projects/:id', element: <ProjectDetailPage /> },

            // Field Ops
            { path: '/field-ops', element: <FieldOpsPage /> },
            { path: '/field-ops/clock', element: <ClockPage /> },
            { path: '/field-ops/daily-log', element: <DailyLogPage /> },
            { path: '/field-ops/camera', element: <CameraPage /> },

            // CRM
            { path: '/crm', element: <CRMPage /> },

            // Placeholder routes — pages to be built
            {
              path: '/financials',
              element: (
                <div className="flex h-64 flex-col items-center justify-center gap-3 text-slate-400">
                  <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm font-medium">Financials — coming soon</p>
                </div>
              ),
            },
            {
              path: '/documents',
              element: (
                <div className="flex h-64 flex-col items-center justify-center gap-3 text-slate-400">
                  <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-sm font-medium">Documents — coming soon</p>
                </div>
              ),
            },
            {
              path: '/scheduling',
              element: (
                <div className="flex h-64 flex-col items-center justify-center gap-3 text-slate-400">
                  <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="text-sm font-medium">Scheduling — coming soon</p>
                </div>
              ),
            },
          ],
        },
      ],
    },
    {
      path: '*',
      element: <Navigate to="/" replace />,
    },
  ],
);
