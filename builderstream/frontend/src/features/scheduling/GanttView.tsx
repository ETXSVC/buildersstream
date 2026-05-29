import { useEffect, useRef, useState, useCallback } from 'react';
import Gantt from 'frappe-gantt';
import { useGanttData } from '@/hooks/useScheduling';
import { useProjects } from '@/hooks/useProjects';
import { patchTaskDates } from '@/api/scheduling';
import { apiClient } from '@/api/client';
import { useQueryClient } from '@tanstack/react-query';

type ViewMode = 'Day' | 'Week' | 'Month';

interface ImpactEntry {
  task_id: string;
  task_name: string;
  old_end: string;
  new_end: string;
  days_shifted: number;
  is_critical_path: boolean;
}

interface ImpactPayload {
  task_id: string;
  task_name: string;
  current_end_date: string | null;
  proposed_end_date: string;
  days_delayed: number;
  affected_tasks: ImpactEntry[];
  affected_count: number;
  critical_path_affected: boolean;
}

interface PendingChange {
  taskId: string;
  startDate: string;
  endDate: string;
  impact: ImpactPayload;
}

function CascadeConfirmModal({
  pending,
  onConfirm,
  onCancel,
}: {
  pending: PendingChange;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const { impact } = pending;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-xl">
        <div className="p-5 border-b border-slate-100">
          <h2 className="text-base font-semibold text-slate-900">Confirm Schedule Change</h2>
          <p className="mt-1 text-sm text-slate-500">
            Moving <strong>{impact.task_name}</strong> to end on{' '}
            <strong>{impact.proposed_end_date}</strong>
            {impact.days_delayed > 0 && ` (+${impact.days_delayed} day${impact.days_delayed !== 1 ? 's' : ''})`}
            {' '}will cascade to {impact.affected_count} downstream task{impact.affected_count !== 1 ? 's' : ''}.
          </p>
          {impact.critical_path_affected && (
            <div className="mt-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 font-medium">
              Critical path tasks affected — project end date may shift.
            </div>
          )}
        </div>

        {impact.affected_tasks.length > 0 && (
          <div className="max-h-56 overflow-y-auto divide-y divide-slate-50">
            {impact.affected_tasks.map((t) => (
              <div key={t.task_id} className="flex items-center justify-between px-5 py-2.5 text-sm">
                <span className="flex items-center gap-2 font-medium text-slate-800">
                  {t.is_critical_path && (
                    <span className="h-2 w-2 rounded-full bg-red-500 shrink-0" title="Critical path" />
                  )}
                  {t.task_name}
                </span>
                <span className="text-xs text-slate-400 shrink-0 ml-4">
                  {t.old_end} → <strong className="text-slate-700">{t.new_end}</strong>
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-end gap-3 p-4 border-t border-slate-100">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600"
          >
            Apply Change
          </button>
        </div>
      </div>
    </div>
  );
}

export const GanttView = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('Week');
  const [pendingChange, setPendingChange] = useState<PendingChange | null>(null);
  const ganttRef = useRef<HTMLDivElement>(null);
  const ganttInstanceRef = useRef<Gantt | null>(null);
  const queryClient = useQueryClient();

  const { data: projects } = useProjects();
  const projectList = projects?.results ?? [];

  const { data: ganttData, isLoading, error } = useGanttData(selectedProjectId || undefined);

  const handleDateChange = useCallback(
    async (task: { id: string; _start: Date; _end: Date }) => {
      const pad = (d: Date) => d.toISOString().split('T')[0];
      const newEnd = pad(task._end);
      const newStart = pad(task._start);

      try {
        // Fetch cascade impact preview first
        const { data: impact } = await apiClient.get<ImpactPayload>(
          `/api/v1/scheduling/tasks/${task.id}/delay-impact/`,
          { params: { new_end_date: newEnd } }
        );

        if (impact.affected_count > 0) {
          // Show confirmation dialog
          setPendingChange({ taskId: task.id, startDate: newStart, endDate: newEnd, impact });
        } else {
          // No downstream impact — save immediately
          await patchTaskDates(task.id, { start_date: newStart, end_date: newEnd });
          queryClient.invalidateQueries({ queryKey: ['gantt', selectedProjectId] });
        }
      } catch {
        // Fall back to saving directly on API error
        try {
          await patchTaskDates(task.id, { start_date: newStart, end_date: newEnd });
          queryClient.invalidateQueries({ queryKey: ['gantt', selectedProjectId] });
        } catch {
          // ignore
        }
      }
    },
    [selectedProjectId, queryClient]
  );

  const handleConfirm = useCallback(async () => {
    if (!pendingChange) return;
    try {
      await patchTaskDates(pendingChange.taskId, {
        start_date: pendingChange.startDate,
        end_date: pendingChange.endDate,
      });
      queryClient.invalidateQueries({ queryKey: ['gantt', selectedProjectId] });
    } catch {
      // ignore
    } finally {
      setPendingChange(null);
    }
  }, [pendingChange, selectedProjectId, queryClient]);

  const handleCancel = useCallback(() => {
    // Re-render Gantt to revert optimistic drag
    queryClient.invalidateQueries({ queryKey: ['gantt', selectedProjectId] });
    setPendingChange(null);
  }, [selectedProjectId, queryClient]);

  useEffect(() => {
    if (!ganttRef.current || !ganttData?.tasks?.length) return;

    // Build frappe-gantt tasks
    const tasks = ganttData.tasks
      .filter((t) => t.start_date && t.end_date)
      .map((t) => ({
        id: t.id,
        name: t.name,
        start: t.start_date!,
        end: t.end_date!,
        progress: t.completion_percentage ?? 0,
        dependencies: ganttData.dependencies
          .filter((d) => d.successor_id === t.id)
          .map((d) => d.predecessor_id)
          .join(','),
        custom_class: t.is_critical_path ? 'gantt-critical' : '',
      }));

    if (!tasks.length) return;

    // Destroy previous instance
    if (ganttRef.current) ganttRef.current.innerHTML = '';

    ganttInstanceRef.current = new Gantt(ganttRef.current, tasks, {
      view_mode: viewMode,
      date_format: 'YYYY-MM-DD',
      popup_trigger: 'click',
      on_date_change: (task: any, start: Date, end: Date) => {
        handleDateChange({ id: task.id, _start: start, _end: end });
      },
      on_progress_change: () => {},
      on_click: () => {},
    });

    return () => {
      if (ganttRef.current) ganttRef.current.innerHTML = '';
      ganttInstanceRef.current = null;
    };
  }, [ganttData, viewMode, handleDateChange]);

  // Update view mode without re-fetching
  useEffect(() => {
    if (ganttInstanceRef.current) {
      ganttInstanceRef.current.change_view_mode(viewMode);
    }
  }, [viewMode]);

  return (
    <div className="flex flex-col gap-4">
      {/* Cascade confirmation modal */}
      {pendingChange && (
        <CascadeConfirmModal
          pending={pendingChange}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">— Select a project —</option>
          {projectList.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <div className="flex rounded-lg border border-slate-200 bg-white overflow-hidden text-sm">
          {(['Day', 'Week', 'Month'] as ViewMode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setViewMode(m)}
              className={[
                'px-3 py-1.5 font-medium transition-colors',
                viewMode === m
                  ? 'bg-blue-500 text-white'
                  : 'text-slate-600 hover:bg-slate-50',
              ].join(' ')}
            >
              {m}
            </button>
          ))}
        </div>

        {ganttData && (
          <span className="ml-auto text-xs text-slate-500">
            {ganttData.stats.completed_tasks}/{ganttData.stats.total_tasks} tasks complete
            &nbsp;·&nbsp;
            {ganttData.stats.average_completion_percentage}% done
            &nbsp;·&nbsp;
            {ganttData.stats.critical_path_tasks} on critical path
          </span>
        )}
      </div>

      {/* States */}
      {!selectedProjectId && (
        <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-16 text-center text-slate-400 text-sm">
          Select a project to view its Gantt chart
        </div>
      )}

      {selectedProjectId && isLoading && (
        <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
          Loading…
        </div>
      )}

      {selectedProjectId && !isLoading && error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load Gantt data.
        </div>
      )}

      {selectedProjectId && !isLoading && !error && ganttData && !ganttData.tasks.filter((t) => t.start_date && t.end_date).length && (
        <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-16 text-center text-slate-400 text-sm">
          No tasks with scheduled dates found for this project.
        </div>
      )}

      {/* Gantt container */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
        <div ref={ganttRef} className="gantt-container" />
      </div>

      {/* Legend */}
      {ganttData?.tasks?.length ? (
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-sm bg-blue-400" />
            Normal task
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-sm bg-red-500" />
            Critical path
          </span>
        </div>
      ) : null}
    </div>
  );
};
