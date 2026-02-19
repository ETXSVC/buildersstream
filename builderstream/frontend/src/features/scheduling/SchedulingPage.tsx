import { useState } from 'react';
import { useTasks, useCrews, useEquipment } from '@/hooks/useScheduling';
import { TASK_STATUS_COLORS, TASK_STATUS_LABELS } from '@/types/scheduling';

type Tab = 'tasks' | 'crews' | 'equipment';

export const SchedulingPage = () => {
  const [tab, setTab] = useState<Tab>('tasks');
  const [search, setSearch] = useState('');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Scheduling</h1>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['tasks', 'crews', 'equipment'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              tab === t ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${tab}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {tab === 'tasks' && <TasksTable search={search} />}
      {tab === 'crews' && <CrewsTable search={search} />}
      {tab === 'equipment' && <EquipmentTable search={search} />}
    </div>
  );
};

function TasksTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30', ordering: 'sort_order' };
  if (search) params.search = search;
  const { data, isLoading } = useTasks(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Task</Th>
            <Th>Project</Th>
            <Th>Start</Th>
            <Th>End</Th>
            <Th>Progress</Th>
            <Th>Crew</Th>
            <Th>Status</Th>
            <Th>CP</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No tasks found.</td></tr>
          )}
          {data?.results.map((task) => (
            <tr key={task.id} className={`hover:bg-slate-50 transition-colors ${task.is_critical_path ? 'border-l-2 border-l-red-400' : ''}`}>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {task.task_type === 'milestone' && (
                    <svg className="h-3.5 w-3.5 flex-shrink-0 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
                    </svg>
                  )}
                  <span className={`font-medium text-slate-900 ${task.task_type === 'summary' ? 'font-semibold' : ''}`}>
                    {task.wbs_code && <span className="mr-1.5 text-xs text-slate-400">{task.wbs_code}</span>}
                    {task.name}
                  </span>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-500 text-xs">{task.project_name}</td>
              <td className="px-4 py-3 text-slate-600">
                {task.start_date ? new Date(task.start_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {task.end_date ? new Date(task.end_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-amber-500"
                      style={{ width: `${task.percent_complete}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500">{task.percent_complete}%</span>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{task.assigned_crew_name ?? '—'}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${TASK_STATUS_COLORS[task.status]}`}>
                  {TASK_STATUS_LABELS[task.status]}
                </span>
              </td>
              <td className="px-4 py-3 text-center">
                {task.is_critical_path && (
                  <span className="text-xs font-bold text-red-500" title="Critical Path">CP</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="tasks" />
    </div>
  );
}

function CrewsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30' };
  if (search) params.search = search;
  const { data, isLoading } = useCrews(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Crew Name</Th>
            <Th>Trade</Th>
            <Th>Foreman</Th>
            <Th>Size</Th>
            <Th>Rate / hr</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No crews found.</td></tr>
          )}
          {data?.results.map((crew) => (
            <tr key={crew.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{crew.name}</td>
              <td className="px-4 py-3 text-slate-600">{crew.trade}</td>
              <td className="px-4 py-3 text-slate-600">{crew.foreman_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-900">{crew.size}</td>
              <td className="px-4 py-3 text-slate-900">
                {crew.hourly_rate ? `$${parseFloat(crew.hourly_rate).toFixed(0)}/hr` : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${crew.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {crew.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="crews" />
    </div>
  );
}

function EquipmentTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30' };
  if (search) params.search = search;
  const { data, isLoading } = useEquipment(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Equipment</Th>
            <Th>Type</Th>
            <Th>Year / Make / Model</Th>
            <Th>Daily Rate</Th>
            <Th>Book Value</Th>
            <Th>Available</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No equipment found.</td></tr>
          )}
          {data?.results.map((eq) => (
            <tr key={eq.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{eq.name}</td>
              <td className="px-4 py-3 text-slate-600">{eq.equipment_type}</td>
              <td className="px-4 py-3 text-slate-600">
                {[eq.year, eq.make, eq.model].filter(Boolean).join(' ') || '—'}
              </td>
              <td className="px-4 py-3 text-slate-900">
                {eq.daily_rate ? `$${parseFloat(eq.daily_rate).toFixed(0)}/day` : '—'}
              </td>
              <td className="px-4 py-3 text-slate-900">
                {eq.current_book_value ? `$${parseFloat(eq.current_book_value).toLocaleString()}` : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${eq.is_available ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                  {eq.is_available ? 'Available' : 'In Use'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="equipment" />
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
      {children}
    </th>
  );
}

function Spinner() {
  return (
    <div className="flex h-40 items-center justify-center">
      <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
    </div>
  );
}

function Pagination({ count, shown, label }: { count?: number; shown?: number; label: string }) {
  if (!count || !shown || count <= shown) return null;
  return (
    <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
      Showing {shown} of {count} {label}
    </div>
  );
}
