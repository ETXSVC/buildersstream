import { WidgetCard } from './WidgetCard';
import type { ActionItem } from '@/types/dashboard';

interface ActionItemsWidgetProps {
  items: ActionItem[];
}

export const ActionItemsWidget = ({ items }: ActionItemsWidgetProps) => {
  const priorityConfig = {
    urgent: {
      label: 'Urgent',
      color: 'text-red-700 bg-red-100',
      icon: '🔥',
    },
    high: {
      label: 'High',
      color: 'text-orange-700 bg-orange-100',
      icon: '⚡',
    },
    medium: {
      label: 'Medium',
      color: 'text-yellow-700 bg-yellow-100',
      icon: '⚠️',
    },
    low: {
      label: 'Low',
      color: 'text-slate-700 bg-slate-100',
      icon: '📌',
    },
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const isOverdue = (dateString: string | null) => {
    if (!dateString) return false;
    return new Date(dateString) < new Date();
  };

  return (
    <WidgetCard
      title="Action Items"
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
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
      }
      action={
        <span className="text-sm font-medium text-slate-600">
          {items.length} item{items.length !== 1 ? 's' : ''}
        </span>
      }
    >
      {items.length === 0 ? (
        <div className="rounded-lg bg-slate-50 p-8 text-center">
          <div className="text-4xl">✅</div>
          <div className="mt-2 text-sm font-medium text-slate-600">
            All caught up!
          </div>
          <div className="mt-1 text-xs text-slate-500">
            No pending action items
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const priority = priorityConfig[item.priority];
            const overdue = isOverdue(item.due_date);

            return (
              <div
                key={item.id}
                className="rounded-lg border border-slate-200 bg-white p-3 transition-shadow hover:shadow-md"
              >
                <div className="flex items-start gap-3">
                  {/* Priority Badge */}
                  <div
                    className={`flex-shrink-0 rounded px-2 py-1 text-xs font-medium ${priority.color}`}
                  >
                    {priority.icon} {priority.label}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-slate-900">
                      {item.title}
                    </div>
                    {item.description && (
                      <div className="mt-1 text-xs text-slate-600 line-clamp-2">
                        {item.description}
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      {item.project_name && (
                        <span className="flex items-center gap-1">
                          <svg
                            className="h-3 w-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                            />
                          </svg>
                          {item.project_name}
                        </span>
                      )}
                      {item.assigned_to_name && (
                        <span className="flex items-center gap-1">
                          <svg
                            className="h-3 w-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                          {item.assigned_to_name}
                        </span>
                      )}
                      {item.due_date && (
                        <span
                          className={`flex items-center gap-1 ${
                            overdue ? 'font-medium text-red-600' : ''
                          }`}
                        >
                          <svg
                            className="h-3 w-3"
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
                          {overdue ? 'Overdue: ' : 'Due: '}
                          {formatDate(item.due_date)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </WidgetCard>
  );
};
