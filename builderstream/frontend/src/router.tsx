import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ResponsiveLayout } from '@/layouts/ResponsiveLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoginPage } from '@/features/auth';
import { DashboardPage } from '@/features/dashboard';

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
            // Field ops mobile routes (pages to be implemented)
            { path: '/field-ops/clock', element: <div className="p-6"><h1 className="text-xl font-semibold">Clock In / Out</h1></div> },
            { path: '/field-ops/daily-log', element: <div className="p-6"><h1 className="text-xl font-semibold">Daily Log</h1></div> },
            { path: '/field-ops/camera', element: <div className="p-6"><h1 className="text-xl font-semibold">Camera</h1></div> },
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
