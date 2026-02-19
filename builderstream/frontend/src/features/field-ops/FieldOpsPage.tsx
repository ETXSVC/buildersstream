/**
 * Desktop/Tablet Field Ops overview — shows time entries and daily logs.
 */
import { Link } from 'react-router-dom';
import { useTimeEntries, useDailyLogs, useOpenTimeEntry } from '@/hooks/useFieldOps';

export const FieldOpsPage = () => {
  const { data: openEntry } = useOpenTimeEntry();
  const { data: entries, isLoading: entriesLoading } = useTimeEntries({ page_size: '10' });
  const { data: logs, isLoading: logsLoading } = useDailyLogs({ page_size: '5' });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Field Operations</h1>

      {/* Clock status banner */}
      <div className={`rounded-xl border p-4 flex items-center justify-between ${
        openEntry ? 'border-green-200 bg-green-50' : 'border-slate-200 bg-white'
      }`}>
        <div>
          <p className="text-sm font-medium text-slate-700">
            {openEntry ? 'Currently clocked in' : 'Not clocked in'}
          </p>
          {openEntry && (
            <p className="text-xs text-slate-500 mt-0.5">
              Since {new Date(openEntry.clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          )}
        </div>
        <Link
          to="/field-ops/clock"
          className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
        >
          {openEntry ? 'Clock Out' : 'Clock In'}
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent time entries */}
        <div className="rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="text-sm font-semibold text-slate-700">Recent Time Entries</h2>
          </div>
          <div className="divide-y divide-slate-50">
            {entriesLoading && (
              <div className="flex h-24 items-center justify-center">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
              </div>
            )}
            {entries?.results.length === 0 && (
              <p className="px-5 py-4 text-sm text-slate-400">No time entries yet.</p>
            )}
            {entries?.results.map((entry) => (
              <div key={entry.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {entry.project_name ?? 'No project'}
                  </p>
                  <p className="text-xs text-slate-500">
                    {new Date(entry.clock_in).toLocaleDateString()}
                    {' · '}
                    {new Date(entry.clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    {entry.clock_out && ' – ' + new Date(entry.clock_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <div className="text-right">
                  {entry.total_hours && (
                    <p className="text-sm font-semibold text-slate-900">{Number(entry.total_hours).toFixed(1)}h</p>
                  )}
                  <span className={`text-xs ${
                    entry.status === 'approved' ? 'text-green-600'
                    : entry.status === 'rejected' ? 'text-red-500'
                    : 'text-slate-400'
                  }`}>
                    {entry.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent daily logs */}
        <div className="rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-100 px-5 py-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-700">Recent Daily Logs</h2>
            <Link to="/field-ops/daily-log" className="text-xs text-amber-600 hover:underline">
              New log
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {logsLoading && (
              <div className="flex h-24 items-center justify-center">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
              </div>
            )}
            {logs?.results.length === 0 && (
              <p className="px-5 py-4 text-sm text-slate-400">No daily logs yet.</p>
            )}
            {logs?.results.map((log) => (
              <div key={log.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">{log.project_name}</p>
                  <p className="text-xs text-slate-500">{new Date(log.log_date).toLocaleDateString()}</p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  log.status === 'approved' ? 'bg-green-100 text-green-700'
                  : log.status === 'submitted' ? 'bg-amber-100 text-amber-700'
                  : 'bg-slate-100 text-slate-600'
                }`}>
                  {log.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
