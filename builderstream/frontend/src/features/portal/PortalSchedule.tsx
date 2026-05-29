import { useQuery } from '@tanstack/react-query';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { fetchPortalSchedule } from '@/api/portal';

export function PortalSchedule() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal', 'schedule'],
    queryFn: fetchPortalSchedule,
    staleTime: 60_000,
  });

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Project Schedule</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load schedule.
        </div>
      )}

      {data && (
        <>
          {/* Project dates */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 grid grid-cols-2 gap-4 sm:grid-cols-3">
            {data.project.start_date && (
              <div>
                <p className="text-xs text-slate-400">Start Date</p>
                <p className="font-semibold text-slate-800">{new Date(data.project.start_date).toLocaleDateString()}</p>
              </div>
            )}
            {data.project.estimated_completion && (
              <div>
                <p className="text-xs text-slate-400">Est. Completion</p>
                <p className="font-semibold text-slate-800">{new Date(data.project.estimated_completion).toLocaleDateString()}</p>
              </div>
            )}
            <div>
              <p className="text-xs text-slate-400">Progress</p>
              <p className="font-semibold text-blue-600">{data.project.percent_complete}% complete</p>
            </div>
          </div>

          {/* Milestones */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100">
              <h2 className="text-sm font-semibold text-slate-700">Milestones</h2>
            </div>

            {data.milestones.length === 0 ? (
              <p className="p-8 text-center text-sm text-slate-400">No milestones yet.</p>
            ) : (
              <div className="divide-y divide-slate-50">
                {data.milestones.map((m) => {
                  const due = m.due_date ? new Date(m.due_date) : null;
                  due?.setHours(0, 0, 0, 0);
                  const isOverdue = !m.is_complete && due && due < today;
                  const isUpcoming = !m.is_complete && due && due >= today;

                  return (
                    <div key={m.id} className="flex items-center gap-4 px-5 py-3.5">
                      <div className="shrink-0">
                        {m.is_complete ? (
                          <CheckCircle size={20} className="text-green-500" />
                        ) : isOverdue ? (
                          <Clock size={20} className="text-red-400" />
                        ) : (
                          <Circle size={20} className="text-slate-300" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${m.is_complete ? 'text-slate-400 line-through' : 'text-slate-900'}`}>
                          {m.name}
                        </p>
                        {m.is_complete && m.completed_at && (
                          <p className="text-xs text-green-600 mt-0.5">
                            Completed {new Date(m.completed_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      {m.due_date && !m.is_complete && (
                        <p className={`text-xs font-medium shrink-0 ${isOverdue ? 'text-red-500' : isUpcoming ? 'text-blue-600' : 'text-slate-400'}`}>
                          {isOverdue ? '⚠ ' : ''}
                          {new Date(m.due_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
