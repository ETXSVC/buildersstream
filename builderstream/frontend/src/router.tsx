import { createBrowserRouter, Navigate, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth';

/** Handles the redirect from the SSO ACS endpoint. Calls hydrate() to pick up
 *  the HttpOnly cookies set by the backend, then navigates into the app. */
function SsoCallbackPage() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const navigate = useNavigate();

  useEffect(() => {
    hydrate().then(() => {
      navigate('/', { replace: true });
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
    </div>
  );
}
import { AuthLayout } from '@/layouts/AuthLayout';
import { ResponsiveLayout } from '@/layouts/ResponsiveLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoginPage } from '@/features/auth';
import { DashboardPage } from '@/features/dashboard';
import { ProjectsPage, ProjectDetailPage, KanbanPage } from '@/features/projects';
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
import { BrandingPage, DunningPage, CustomFieldsPage, IntegrationsPage } from '@/features/settings';
import { CollaborationPage } from '@/features/collaboration';
import { IssuesPage } from '@/features/issues';
import { CompanyPage } from '@/features/company/CompanyPage';
import { PayInvoicePage } from '@/features/financials/PayInvoicePage';
import { PortalLoginPage } from '@/features/portal/PortalLoginPage';
import { PortalLayout } from '@/features/portal/PortalLayout';
import { PortalDashboard } from '@/features/portal/PortalDashboard';
import { PortalApprovals } from '@/features/portal/PortalApprovals';
import { PortalSelections } from '@/features/portal/PortalSelections';
import { PortalMessages } from '@/features/portal/PortalMessages';
import { PortalSchedule } from '@/features/portal/PortalSchedule';
import { PortalDocuments } from '@/features/portal/PortalDocuments';
import { PortalPhotos } from '@/features/portal/PortalPhotos';

export const router = createBrowserRouter(
  [
    {
      // Public routes — no authentication required
      children: [
        { path: '/pay/:token', element: <PayInvoicePage /> },
        { path: '/portal/login', element: <PortalLoginPage /> },
        { path: '/portal', element: <Navigate to="/portal/login" replace /> },
        { path: '/sso-callback', element: <SsoCallbackPage /> },
      ],
    },
    {
      // Client portal — own layout, portal JWT auth
      element: <PortalLayout />,
      children: [
        { path: '/portal/dashboard', element: <PortalDashboard /> },
        { path: '/portal/approvals', element: <PortalApprovals /> },
        { path: '/portal/selections', element: <PortalSelections /> },
        { path: '/portal/messages', element: <PortalMessages /> },
        { path: '/portal/schedule', element: <PortalSchedule /> },
        { path: '/portal/documents', element: <PortalDocuments /> },
        { path: '/portal/photos', element: <PortalPhotos /> },
      ],
    },
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
            { path: '/projects/kanban', element: <KanbanPage /> },
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

            // Collaboration / Team Chat
            { path: '/company', element: <CompanyPage /> },
            { path: '/collaboration', element: <CollaborationPage /> },

            // Issue Tracking
            { path: '/issues', element: <IssuesPage /> },

            // Settings
            { path: '/settings/branding', element: <BrandingPage /> },
            { path: '/settings/dunning', element: <DunningPage /> },
            { path: '/settings/custom-fields', element: <CustomFieldsPage /> },
            { path: '/settings/integrations', element: <IntegrationsPage /> },
          ],
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
      v7_relativeSplatPath: true,
    },
  },
);
