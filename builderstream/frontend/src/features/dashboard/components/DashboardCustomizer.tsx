import { useState, useRef } from 'react';
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
  const dragIndex = useRef<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  if (!isOpen) return null;

  const handleToggleVisibility = (widgetId: string) => {
    setLocalWidgets((prev) =>
      prev.map((w) =>
        w.id === widgetId ? { ...w, isVisible: !w.isVisible } : w,
      ),
    );
  };

  const handleDragStart = (index: number) => {
    dragIndex.current = index;
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (dragIndex.current !== null && dragIndex.current !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    const fromIndex = dragIndex.current;
    if (fromIndex === null || fromIndex === dropIndex) {
      dragIndex.current = null;
      setDragOverIndex(null);
      return;
    }
    setLocalWidgets((prev) => {
      const next = [...prev];
      const [moved] = next.splice(fromIndex, 1);
      next.splice(dropIndex, 0, moved);
      // Re-assign y positions to match new order
      return next.map((w, i) => ({ ...w, y: i }));
    });
    dragIndex.current = null;
    setDragOverIndex(null);
  };

  const handleDragEnd = () => {
    dragIndex.current = null;
    setDragOverIndex(null);
  };

  const handleSave = () => {
    onSave(localWidgets);
    onClose();
  };

  const handleCancel = () => {
    setLocalWidgets(widgets);
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
            type="button"
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
          <p className="mb-1 text-sm text-slate-600">
            Toggle widgets on or off and drag to reorder.
          </p>
          <p className="mb-4 flex items-center gap-1.5 text-xs text-slate-400">
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 8h16M4 16h16" />
            </svg>
            Drag the handle on the left to reorder
          </p>

          <div className="space-y-2">
            {localWidgets.map((widget, index) => (
              <div
                key={widget.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDrop={(e) => handleDrop(e, index)}
                onDragEnd={handleDragEnd}
                className={[
                  'flex items-center justify-between rounded-lg border bg-white p-3 transition-all',
                  dragOverIndex === index && dragIndex.current !== index
                    ? 'border-amber-400 bg-amber-50 shadow-md'
                    : dragIndex.current === index
                    ? 'border-slate-300 opacity-50'
                    : 'border-slate-200 hover:border-slate-300',
                ].join(' ')}
              >
                {/* Drag handle */}
                <div className="mr-2 cursor-grab touch-none text-slate-300 active:cursor-grabbing">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 9h16.5m-16.5 6.75h16.5" />
                  </svg>
                </div>

                {/* Icon + label */}
                <div className="flex flex-1 items-center gap-3">
                  <div
                    className={`flex h-9 w-9 items-center justify-center rounded-lg text-lg ${
                      widget.isVisible
                        ? 'bg-amber-50 text-amber-600'
                        : 'bg-slate-100 text-slate-300'
                    }`}
                  >
                    {getWidgetIcon(widget.type)}
                  </div>
                  <div>
                    <div className={`text-sm font-medium ${widget.isVisible ? 'text-slate-900' : 'text-slate-400'}`}>
                      {widget.title}
                    </div>
                    <div className="text-xs text-slate-400">
                      {getWidgetDescription(widget.type)}
                    </div>
                  </div>
                </div>

                {/* Toggle */}
                <button
                  type="button"
                  onClick={() => handleToggleVisibility(widget.id)}
                  aria-label={widget.isVisible ? 'Hide widget' : 'Show widget'}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors ${
                    widget.isVisible ? 'bg-amber-500' : 'bg-slate-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                      widget.isVisible ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button
            type="button"
            onClick={handleCancel}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
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
