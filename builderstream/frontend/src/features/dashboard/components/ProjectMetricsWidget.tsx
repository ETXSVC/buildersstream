import { WidgetCard } from './WidgetCard';
import type { ProjectMetrics } from '@/types/dashboard';

interface ProjectMetricsWidgetProps {
  metrics: ProjectMetrics;
}

export const ProjectMetricsWidget = ({
  metrics,
}: ProjectMetricsWidgetProps) => {
  const healthTotal =
    metrics.health_distribution.green +
    metrics.health_distribution.yellow +
    metrics.health_distribution.red;

  const healthPercent = (count: number) =>
    healthTotal > 0 ? Math.round((count / healthTotal) * 100) : 0;

  return (
    <WidgetCard
      title="Project Overview"
      icon={
        <svg
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      }
    >
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <MetricCard
          label="Total Projects"
          value={metrics.total_projects}
          className="bg-slate-50"
        />
        <MetricCard
          label="Active"
          value={metrics.active_projects}
          className="bg-blue-50 text-blue-700"
        />
        <MetricCard
          label="On Hold"
          value={metrics.on_hold_projects}
          className="bg-yellow-50 text-yellow-700"
        />
        <MetricCard
          label="Completed"
          value={metrics.completed_projects}
          className="bg-green-50 text-green-700"
        />
      </div>

      {/* Health Distribution */}
      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-medium text-slate-700">Project Health</span>
          <span className="text-slate-500">{healthTotal} projects</span>
        </div>
        <div className="flex h-3 overflow-hidden rounded-full bg-slate-100">
          {metrics.health_distribution.green > 0 && (
            <div
              className="bg-green-500"
              style={{ width: `${healthPercent(metrics.health_distribution.green)}%` }}
              title={`${metrics.health_distribution.green} healthy`}
            />
          )}
          {metrics.health_distribution.yellow > 0 && (
            <div
              className="bg-yellow-500"
              style={{ width: `${healthPercent(metrics.health_distribution.yellow)}%` }}
              title={`${metrics.health_distribution.yellow} at risk`}
            />
          )}
          {metrics.health_distribution.red > 0 && (
            <div
              className="bg-red-500"
              style={{ width: `${healthPercent(metrics.health_distribution.red)}%` }}
              title={`${metrics.health_distribution.red} critical`}
            />
          )}
        </div>
        <div className="mt-2 flex justify-between text-xs text-slate-600">
          <span>
            🟢 {metrics.health_distribution.green} Healthy
          </span>
          <span>
            🟡 {metrics.health_distribution.yellow} At Risk
          </span>
          <span>
            🔴 {metrics.health_distribution.red} Critical
          </span>
        </div>
      </div>

      {/* Status Breakdown */}
      {Object.keys(metrics.by_status).length > 0 && (
        <div className="mt-6">
          <h4 className="mb-3 text-sm font-medium text-slate-700">
            By Status
          </h4>
          <div className="space-y-2">
            {Object.entries(metrics.by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <span className="text-sm capitalize text-slate-600">
                  {status.replace('_', ' ')}
                </span>
                <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-sm font-medium text-slate-700">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </WidgetCard>
  );
};

interface MetricCardProps {
  label: string;
  value: number;
  className?: string;
}

const MetricCard = ({ label, value, className = '' }: MetricCardProps) => (
  <div className={`rounded-lg p-3 ${className}`}>
    <div className="text-2xl font-bold">{value}</div>
    <div className="text-xs font-medium opacity-75">{label}</div>
  </div>
);
