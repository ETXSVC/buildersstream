import { WidgetCard } from './WidgetCard';
import type { ScheduleOverview } from '@/types/dashboard';

interface ScheduleOverviewWidgetProps {
  schedule: ScheduleOverview;
}

export const ScheduleOverviewWidget = ({
  schedule,
}: ScheduleOverviewWidgetProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const getDaysUntil = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  return (
    <WidgetCard
      title="Schedule Overview"
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
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      }
    >
      {/* Overdue Tasks Alert */}
      {schedule.overdue_tasks_count > 0 && (
        <div className="mb-4 flex items-center gap-3 rounded-lg bg-red-50 p-3">
          <svg
            className="h-5 w-5 flex-shrink-0 text-red-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div className="flex-1">
            <div className="text-sm font-medium text-red-900">
              {schedule.overdue_tasks_count} Overdue Task
              {schedule.overdue_tasks_count !== 1 ? 's' : ''}
            </div>
            <div className="text-xs text-red-700">
              Requires immediate attention
            </div>
          </div>
        </div>
      )}

      {/* Upcoming Milestones */}
      <div>
        <h4 className="mb-3 text-sm font-medium text-slate-700">
          Upcoming Milestones
        </h4>
        {schedule.upcoming_milestones.length === 0 ? (
          <div className="rounded-lg bg-slate-50 p-4 text-center text-sm text-slate-500">
            No upcoming milestones
          </div>
        ) : (
          <div className="space-y-2">
            {schedule.upcoming_milestones.slice(0, 5).map((milestone) => {
              const daysUntil = getDaysUntil(milestone.due_date);
              const isOverdue = milestone.is_overdue;
              const urgencyColor = isOverdue
                ? 'border-red-200 bg-red-50'
                : daysUntil <= 3
                  ? 'border-orange-200 bg-orange-50'
                  : 'border-slate-200 bg-white';

              return (
                <div
                  key={milestone.id}
                  className={`rounded-lg border p-3 ${urgencyColor}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-slate-900">
                        {milestone.name}
                      </div>
                      <div className="mt-1 text-xs text-slate-600">
                        {milestone.project_name}
                      </div>
                    </div>
                    <div className="ml-3 text-right">
                      <div
                        className={`text-xs font-medium ${
                          isOverdue
                            ? 'text-red-700'
                            : daysUntil <= 3
                              ? 'text-orange-700'
                              : 'text-slate-700'
                        }`}
                      >
                        {formatDate(milestone.due_date)}
                      </div>
                      <div className="mt-0.5 text-xs text-slate-500">
                        {isOverdue
                          ? `${Math.abs(daysUntil)} days overdue`
                          : daysUntil === 0
                            ? 'Due today'
                            : daysUntil === 1
                              ? 'Due tomorrow'
                              : `${daysUntil} days`}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Crew Availability */}
      {schedule.crew_availability.length > 0 && (
        <div className="mt-6">
          <h4 className="mb-3 text-sm font-medium text-slate-700">
            Crew Availability
          </h4>
          <div className="space-y-2">
            {schedule.crew_availability.map((crew) => {
              const utilization = parseFloat(crew.utilization_pct);
              const utilizationColor =
                utilization >= 90
                  ? 'bg-red-500'
                  : utilization >= 70
                    ? 'bg-yellow-500'
                    : 'bg-green-500';

              return (
                <div key={crew.crew_name}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="font-medium text-slate-700">
                      {crew.crew_name}
                    </span>
                    <span className="text-slate-600">
                      {crew.available}/{crew.total} available ({crew.utilization_pct}%)
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full ${utilizationColor}`}
                      style={{ width: `${utilization}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </WidgetCard>
  );
};
