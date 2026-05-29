import { WidgetCard } from './WidgetCard';
import type { ActivityLogEntry } from '@/types/dashboard';

interface ActivityStreamWidgetProps {
  activities: ActivityLogEntry[];
}

export const ActivityStreamWidget = ({
  activities,
}: ActivityStreamWidgetProps) => {
  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const getActionIcon = (action: string) => {
    const iconMap: Record<string, string> = {
      created: '➕',
      updated: '✏️',
      deleted: '🗑️',
      status_changed: '🔄',
      assigned: '👤',
      completed: '✅',
      approved: '✓',
      rejected: '✗',
      comment: '💬',
      upload: '📎',
      download: '📥',
    };
    return iconMap[action] || '📝';
  };

  const getActionColor = (action: string) => {
    const colorMap: Record<string, string> = {
      created: 'bg-green-100 text-green-700',
      updated: 'bg-blue-100 text-blue-700',
      deleted: 'bg-red-100 text-red-700',
      status_changed: 'bg-purple-100 text-purple-700',
      assigned: 'bg-indigo-100 text-indigo-700',
      completed: 'bg-green-100 text-green-700',
      approved: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      comment: 'bg-slate-100 text-slate-700',
      upload: 'bg-blue-100 text-blue-700',
    };
    return colorMap[action] || 'bg-slate-100 text-slate-700';
  };

  return (
    <WidgetCard
      title="Recent Activity"
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
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      }
    >
      {activities.length === 0 ? (
        <div className="rounded-lg bg-slate-50 p-8 text-center text-sm text-slate-500">
          No recent activity
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((activity, index) => (
            <div
              key={activity.id}
              className={`flex gap-3 ${
                index !== activities.length - 1
                  ? 'border-b border-slate-100 pb-3'
                  : ''
              }`}
            >
              {/* Icon */}
              <div
                className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm ${getActionColor(activity.action)}`}
              >
                {getActionIcon(activity.action)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm">
                      <span className="font-medium text-slate-900">
                        {activity.user_name}
                      </span>{' '}
                      <span className="text-slate-600">
                        {activity.description}
                      </span>
                    </div>

                    {/* Entity Type Badge */}
                    <div className="mt-1 flex items-center gap-2">
                      <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium capitalize text-slate-700">
                        {activity.entity_type.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-slate-500">
                        {formatTimeAgo(activity.timestamp)}
                      </span>
                    </div>

                    {/* Metadata Preview */}
                    {activity.metadata &&
                      Object.keys(activity.metadata).length > 0 && (
                        <div className="mt-1 text-xs text-slate-500">
                          {Object.entries(activity.metadata)
                            .slice(0, 2)
                            .map(([key, value]) => (
                              <span key={key} className="mr-3">
                                {key}: {String(value)}
                              </span>
                            ))}
                        </div>
                      )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </WidgetCard>
  );
};
