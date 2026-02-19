import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import {
  useDashboard,
  useRefreshDashboard,
  useDashboardLayout,
  useUpdateDashboardLayout,
} from '@/hooks/useDashboard';
import { ProjectMetricsWidget } from './components/ProjectMetricsWidget';
import { FinancialSummaryWidget } from './components/FinancialSummaryWidget';
import { ScheduleOverviewWidget } from './components/ScheduleOverviewWidget';
import { ActionItemsWidget } from './components/ActionItemsWidget';
import { ActivityStreamWidget } from './components/ActivityStreamWidget';
import { DashboardCustomizer } from './components/DashboardCustomizer';
import type { Widget } from '@/types/dashboard';

const DEFAULT_WIDGETS: Widget[] = [
  { id: 'projects', type: 'projects', title: 'Project Overview', x: 0, y: 0, width: 2, height: 1, isVisible: true },
  { id: 'financial', type: 'financial', title: 'Financial Summary', x: 2, y: 0, width: 1, height: 1, isVisible: true },
  { id: 'schedule', type: 'schedule', title: 'Schedule Overview', x: 0, y: 1, width: 2, height: 1, isVisible: true },
  { id: 'actions', type: 'actions', title: 'Action Items', x: 2, y: 1, width: 1, height: 1, isVisible: true },
  { id: 'activity', type: 'activity', title: 'Recent Activity', x: 0, y: 2, width: 3, height: 1, isVisible: true },
];

export const DashboardPage = () => {
  const { user, organizations, currentOrganizationId } = useAuth();
  const { data: dashboard, isLoading, error } = useDashboard();
  const { data: layout } = useDashboardLayout();
  const updateLayout = useUpdateDashboardLayout();
  const refreshDashboard = useRefreshDashboard();
  const [isCustomizing, setIsCustomizing] = useState(false);

  const currentOrg = organizations.find(
    (o) => o.organization_id === currentOrganizationId,
  );

  // Get widget visibility from layout (or show all by default)
  const widgetVisibility: Record<string, boolean> = {};
  if (layout?.widgets) {
    layout.widgets.forEach((w) => {
      widgetVisibility[w.type] = w.isVisible;
    });
  } else {
    // Default: all visible
    ['projects', 'financial', 'schedule', 'actions', 'activity'].forEach(
      (type) => {
        widgetVisibility[type] = true;
      },
    );
  }

  const handleSaveCustomization = (widgets: Widget[]) => {
    updateLayout.mutate({
      widgets: widgets.map((w) => ({
        type: w.type,
        x: w.x,
        y: w.y,
        width: w.width,
        height: w.height,
        minWidth: w.minWidth,
        minHeight: w.minHeight,
        isVisible: w.isVisible,
      })),
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-4 text-sm text-slate-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="mt-4 text-lg font-medium text-red-900">
            Failed to load dashboard
          </p>
          <p className="mt-2 text-sm text-red-700">
            {error instanceof Error ? error.message : 'An error occurred'}
          </p>
          <button
            onClick={refreshDashboard}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // No data state
  if (!dashboard) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-slate-600">No dashboard data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Welcome back, {user?.first_name}!
            </h1>
            {currentOrg && (
              <p className="mt-1 text-sm text-slate-600">
                {currentOrg.organization_name} &middot;{' '}
                <span className="capitalize">
                  {currentOrg.role.replace('_', ' ')}
                </span>
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsCustomizing(true)}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              title="Customize dashboard"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                />
              </svg>
            </button>
            <button
              type="button"
              onClick={refreshDashboard}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              title="Refresh dashboard"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
        {dashboard.cached_at && (
          <p className="mt-2 text-xs text-slate-500">
            Last updated: {new Date(dashboard.cached_at).toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {/* Projects - Full width on mobile, 2 cols on lg */}
        {widgetVisibility.projects !== false && (
          <div className="lg:col-span-2">
            <ProjectMetricsWidget metrics={dashboard.project_metrics} />
          </div>
        )}

        {/* Financial - 1 col */}
        {widgetVisibility.financial !== false && (
          <div>
            <FinancialSummaryWidget financial={dashboard.financial_summary} />
          </div>
        )}

        {/* Schedule - Full width on mobile, 2 cols on lg */}
        {widgetVisibility.schedule !== false && (
          <div className="lg:col-span-2">
            <ScheduleOverviewWidget schedule={dashboard.schedule_overview} />
          </div>
        )}

        {/* Action Items - 1 col */}
        {widgetVisibility.actions !== false && (
          <div>
            <ActionItemsWidget items={dashboard.action_items} />
          </div>
        )}

        {/* Activity Stream - Full width */}
        {widgetVisibility.activity !== false && (
          <div className="lg:col-span-2 xl:col-span-3">
            <ActivityStreamWidget activities={dashboard.activity_stream} />
          </div>
        )}
      </div>

      {/* Customizer Modal */}
      <DashboardCustomizer
        isOpen={isCustomizing}
        onClose={() => setIsCustomizing(false)}
        widgets={layout?.widgets?.length ? layout.widgets : DEFAULT_WIDGETS}
        onSave={handleSaveCustomization}
      />
    </div>
  );
};
