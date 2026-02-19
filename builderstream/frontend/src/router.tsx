import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ResponsiveLayout } from '@/layouts/ResponsiveLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoginPage } from '@/features/auth';
import { DashboardPage } from '@/features/dashboard';
import { ProjectsPage, ProjectDetailPage } from '@/features/projects';
import { ClockPage, DailyLogPage, CameraPage, FieldOpsPage } from '@/features/field-ops';
import { CRMPage } from '@/features/crm';
import { FinancialsPage } from '@/features/financials';
import { SchedulingPage } from '@/features/scheduling';
import { DocumentsPage } from '@/features/documents';
import { EstimatingPage } from '@/features/estimating';
import { AnalyticsPage } from '@/features/analytics';
import { QualitySafetyPage } from '@/features/quality-safety';
import { PayrollPage } from '@/features/payroll';
import { ServicePage } from '@/features/service';

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

            // Financials
            { path: '/financials', element: <FinancialsPage /> },

            // Scheduling
            { path: '/scheduling', element: <SchedulingPage /> },

            // Documents
            { path: '/documents', element: <DocumentsPage /> },

            // Estimating
            { path: '/estimating', element: <EstimatingPage /> },

            // Analytics
            { path: '/analytics', element: <AnalyticsPage /> },

            // Quality & Safety
            { path: '/quality-safety', element: <QualitySafetyPage /> },

            // Payroll
            { path: '/payroll', element: <PayrollPage /> },

            // Service & Warranty
            { path: '/service', element: <ServicePage /> },
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
