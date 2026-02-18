import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/layouts/AuthLayout';
import { AppLayout } from '@/layouts/AppLayout';
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
          element: <AppLayout />,
          children: [{ path: '/', element: <DashboardPage /> }],
        },
      ],
    },
    {
      path: '*',
      element: <Navigate to="/" replace />,
    },
  ],
  {
    future: {
      v7_startTransition: true,
    },
  },
);
