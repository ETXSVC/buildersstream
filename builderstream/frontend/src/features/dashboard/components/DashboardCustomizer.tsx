import { useState } from 'react';
import type { Widget } from '@/types/dashboard';

interface DashboardCustomizerProps {
  isOpen: boolean;
  onClose: () => void;
  widgets: Widget[];
  onSave: (widgets: Widget[]) => void;
}

export const DashboardCustomizer = ({
  isOpen,
  onClose,
  widgets,
  onSave,
}: DashboardCustomizerProps) => {
  const [localWidgets, setLocalWidgets] = useState(widgets);

  if (!isOpen) return null;

  const handleToggleVisibility = (widgetId: string) => {
    setLocalWidgets((prev) =>
      prev.map((w) =>
        w.id === widgetId ? { ...w, isVisible: !w.isVisible } : w,
      ),
    );
  };

  const handleSave = () => {
    onSave(localWidgets);
    onClose();
  };

  const handleCancel = () => {
    setLocalWidgets(widgets); // Reset to original
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">
            Customize Dashboard
          </h2>
          <button
            onClick={handleCancel}
            className="text-slate-400 hover:text-slate-600"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="mb-4 text-sm text-slate-600">
            Toggle widgets on or off to customize your dashboard view.
          </p>

          <div className="space-y-3">
            {localWidgets.map((widget) => (
              <div
                key={widget.id}
                className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-4"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                      widget.isVisible
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-slate-200 text-slate-400'
                    }`}
                  >
                    {getWidgetIcon(widget.type)}
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">
                      {widget.title}
                    </div>
                    <div className="text-xs text-slate-500">
                      {getWidgetDescription(widget.type)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleToggleVisibility(widget.id)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    widget.isVisible ? 'bg-blue-600' : 'bg-slate-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      widget.isVisible ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
            💡 <strong>Coming soon:</strong> Drag and drop to rearrange widgets!
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button
            onClick={handleCancel}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

function getWidgetIcon(type: string) {
  const icons: Record<string, string> = {
    projects: '📊',
    financial: '💰',
    schedule: '📅',
    actions: '✓',
    activity: '🕐',
  };
  return icons[type] || '📋';
}

function getWidgetDescription(type: string) {
  const descriptions: Record<string, string> = {
    projects: 'Project metrics and health overview',
    financial: 'Budget, revenue, and costs summary',
    schedule: 'Milestones and crew availability',
    actions: 'Your top priority action items',
    activity: 'Recent project activity stream',
  };
  return descriptions[type] || 'Dashboard widget';
}
