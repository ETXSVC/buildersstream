import { useState, useEffect, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import { GanttView } from './GanttView';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useTasks, useCrews, useEquipment,
  useCreateTask, useUpdateTask, useDeleteTask,
  useCreateCrew, useUpdateCrew, useDeleteCrew,
  useCreateEquipment, useUpdateEquipment, useDeleteEquipment,
} from '@/hooks/useScheduling';
import { useProjects } from '@/hooks/useProjects';
import { useOrgMembers } from '@/hooks/useScheduling';
import { useEmployees } from '@/hooks/usePayroll';
import { TASK_STATUS_COLORS, TASK_STATUS_LABELS, type Task, type Crew, type Equipment } from '@/types/scheduling';

type Tab = 'tasks' | 'crews' | 'equipment' | 'gantt';

function SchedulingDashboard() {
  const { data: tasksData } = useTasks({});
  const { data: crewsData } = useCrews({});
  const { data: equipmentData } = useEquipment({});

  const stats = useMemo(() => {
    const tasks = tasksData?.results ?? [];
    const total = tasks.length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const completed = tasks.filter(t => t.status === 'completed').length;
    const today = new Date().toISOString().split('T')[0];
    const overdue = tasks.filter(t => t.status !== 'completed' && t.status !== 'canceled' && t.end_date && t.end_date < today).length;
    const statusCounts = tasks.reduce<Record<string, number>>((acc, t) => {
      acc[t.status] = (acc[t.status] ?? 0) + 1;
      return acc;
    }, {});
    const crews = crewsData?.results?.length ?? 0;
    const equip = equipmentData?.results?.length ?? 0;
    return { total, inProgress, completed, overdue, statusCounts, crews, equip };
  }, [tasksData, crewsData, equipmentData]);

  const STATUS_LABELS: Record<string, string> = {
    not_started: 'Not Started', in_progress: 'In Progress',
    completed: 'Completed', on_hold: 'On Hold', canceled: 'Canceled',
  };
  const STATUS_COLORS_MAP: Record<string, string> = {
    not_started: '#94a3b8', in_progress: '#60a5fa',
    completed: '#22c55e', on_hold: '#f59e0b', canceled: '#e2e8f0',
  };

  const statusData = Object.entries(stats.statusCounts).map(([k, v]) => ({
    name: STATUS_LABELS[k] ?? k,
    value: v,
    color: STATUS_COLORS_MAP[k] ?? '#94a3b8',
  }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Total Tasks" value={stats.total} icon="📋" />
        <KpiCard label="In Progress" value={stats.inProgress} icon="⚡" accent="blue" />
        <KpiCard label="Completed" value={stats.completed} icon="✅" accent="green" />
        <KpiCard label="Overdue" value={stats.overdue} icon="⚠️" accent={stats.overdue > 0 ? 'red' : 'default'} sub={`${stats.crews} crews · ${stats.equip} equipment`} />
      </div>
      {statusData.length > 0 && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Task Status Breakdown</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={statusData} margin={{ top: 0, right: 8, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {statusData.map(e => <Cell key={e.name} fill={e.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Task Distribution</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70}>
                  {statusData.map(e => <Cell key={e.name} fill={e.color} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export const SchedulingPage = () => {
  const [tab, setTab] = useState<Tab>('tasks');
  const [search, setSearch] = useState('');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Scheduling</h1>
        {tab === 'tasks' && <NewTaskButton />}
        {tab === 'crews' && <NewCrewButton />}
        {tab === 'equipment' && <NewEquipmentButton />}
      </div>
      <SchedulingDashboard />

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['tasks', 'gantt', 'crews', 'equipment'] as Tab[]).map((t) => (
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

      {tab !== 'gantt' && (
        <div className="mb-4">
          <input
            type="search"
            placeholder={`Search ${tab}…`}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
          />
        </div>
      )}

      {tab === 'tasks' && <TasksTable search={search} />}
      {tab === 'gantt' && <GanttView />}
      {tab === 'crews' && <CrewsTable search={search} />}
      {tab === 'equipment' && <EquipmentTable search={search} />}
    </div>
  );
};

// ─── New buttons ──────────────────────────────────────────────────────────────

function NewTaskButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={btnCls}>
        <span className="text-lg leading-none">+</span> New Task
      </button>
      {open && <TaskModal onClose={() => setOpen(false)} />}
    </>
  );
}

function NewCrewButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={btnCls}>
        <span className="text-lg leading-none">+</span> New Crew
      </button>
      {open && <CrewModal onClose={() => setOpen(false)} />}
    </>
  );
}

function NewEquipmentButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={btnCls}>
        <span className="text-lg leading-none">+</span> New Equipment
      </button>
      {open && <EquipmentModal onClose={() => setOpen(false)} />}
    </>
  );
}

// ─── Tables ──────────────────────────────────────────────────────────────────

function TasksTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30', ordering: 'sort_order' };
  if (search) params.search = search;
  const { data, isLoading } = useTasks(params);
  const deleteTask = useDeleteTask();
  const [editing, setEditing] = useState<Task | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No tasks found.</td></tr>
            )}
            {data?.results.map((task) => (
              <tr key={task.id} className={`group hover:bg-slate-50 transition-colors ${task.is_critical_path ? 'border-l-2 border-l-red-400' : ''}`}>
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
                  {fmtDate(task.start_date)}
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {fmtDate(task.end_date)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-amber-500 [width:var(--p)]"
                        style={{ '--p': `${task.completion_percentage}%` } as React.CSSProperties}
                      />
                    </div>
                    <span className="text-xs text-slate-500">{task.completion_percentage}%</span>
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
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(task)}
                    onDelete={() => { if (confirm('Delete this task?')) deleteTask.mutate(task.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="tasks" />
      </div>
      {editing && <TaskModal task={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

function CrewsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30' };
  if (search) params.search = search;
  const { data, isLoading } = useCrews(params);
  const deleteCrew = useDeleteCrew();
  const [editing, setEditing] = useState<Crew | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No crews found.</td></tr>
            )}
            {data?.results.map((crew) => (
              <tr key={crew.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">{crew.name}</td>
                <td className="px-4 py-3 text-slate-600">{crew.trade}</td>
                <td className="px-4 py-3 text-slate-600">{crew.foreman_name ?? '—'}</td>
                <td className="px-4 py-3 text-slate-900">{crew.member_count}</td>
                <td className="px-4 py-3 text-slate-900">
                  {crew.hourly_rate ? `$${parseFloat(crew.hourly_rate).toFixed(0)}/hr` : '—'}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${crew.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                    {crew.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(crew)}
                    onDelete={() => { if (confirm('Delete this crew?')) deleteCrew.mutate(crew.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="crews" />
      </div>
      {editing && <CrewModal crew={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

function EquipmentTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '30' };
  if (search) params.search = search;
  const { data, isLoading } = useEquipment(params);
  const deleteEq = useDeleteEquipment();
  const [editing, setEditing] = useState<Equipment | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No equipment found.</td></tr>
            )}
            {data?.results.map((eq) => (
              <tr key={eq.id} className="group hover:bg-slate-50 transition-colors">
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
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(eq)}
                    onDelete={() => { if (confirm('Delete this equipment?')) deleteEq.mutate(eq.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="equipment" />
      </div>
      {editing && <EquipmentModal equipment={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

// ─── Modals ───────────────────────────────────────────────────────────────────

function TaskModal({ task, onClose }: { task?: Task; onClose: () => void }) {
  const { data: projectsData } = useProjects();
  const { data: crewsData } = useCrews();
  const create = useCreateTask();
  const update = useUpdateTask();
  const isEdit = !!task;

  const [form, setForm] = useState({
    project: task?.project ?? '',
    name: task?.name ?? '',
    task_type: task?.task_type ?? 'task',
    status: task?.status ?? 'not_started',
    start_date: task?.start_date ?? '',
    end_date: task?.end_date ?? '',
    estimated_hours: task?.estimated_hours ? String(task.estimated_hours) : '',
    completion_percentage: task?.completion_percentage ? String(task.completion_percentage) : '0',
    assigned_crew: task?.assigned_crew ?? '',
  });

  useEffect(() => {
    setForm({
      project: task?.project ?? '',
      name: task?.name ?? '',
      task_type: task?.task_type ?? 'task',
      status: task?.status ?? 'not_started',
      start_date: task?.start_date ?? '',
      end_date: task?.end_date ?? '',
      estimated_hours: task?.estimated_hours ? String(task.estimated_hours) : '',
      completion_percentage: String(task?.completion_percentage ?? 0),
      assigned_crew: task?.assigned_crew ?? '',
    });
  }, [task]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      name: form.name,
      task_type: form.task_type,
      status: form.status,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      estimated_hours: form.estimated_hours ? parseFloat(form.estimated_hours) : null,
      completion_percentage: parseInt(form.completion_percentage) || 0,
    };
    if (!isEdit && form.project) payload.project = form.project;
    if (form.assigned_crew) payload.assigned_crew = form.assigned_crew;
    if (isEdit) {
      update.mutate({ id: task.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit Task' : 'New Task'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isEdit && (
          <Field label="Project *">
            <select
              title="Project"
              required
              value={form.project}
              onChange={(e) => setForm((f) => ({ ...f, project: e.target.value }))}
              className={selectCls}
            >
              <option value="">Select project…</option>
              {projectsData?.results.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </Field>
        )}
        <Field label="Task Name *">
          <input
            type="text"
            title="Task Name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className={inputCls}
            placeholder="Task name…"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Type">
            <select
              title="Task Type"
              value={form.task_type}
              onChange={(e) => setForm((f) => ({ ...f, task_type: e.target.value }))}
              className={selectCls}
            >
              {['task', 'milestone', 'summary', 'deliverable'].map((t) => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select
              title="Status"
              value={form.status}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className={selectCls}
            >
              {Object.entries(TASK_STATUS_LABELS).map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Start Date">
            <input
              type="date"
              title="Start Date"
              value={form.start_date}
              onChange={(e) => setForm((f) => ({ ...f, start_date: e.target.value }))}
              className={inputCls}
            />
          </Field>
          <Field label="End Date">
            <input
              type="date"
              title="End Date"
              value={form.end_date}
              onChange={(e) => setForm((f) => ({ ...f, end_date: e.target.value }))}
              className={inputCls}
            />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Estimated Hours">
            <input
              type="number"
              title="Estimated Hours"
              step="0.5"
              value={form.estimated_hours}
              onChange={(e) => setForm((f) => ({ ...f, estimated_hours: e.target.value }))}
              className={inputCls}
              placeholder="0"
            />
          </Field>
          <Field label="% Complete">
            <input
              type="number"
              title="Percent Complete"
              min="0"
              max="100"
              value={form.completion_percentage}
              onChange={(e) => setForm((f) => ({ ...f, completion_percentage: e.target.value }))}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Assigned Crew">
          <select
            title="Assigned Crew"
            value={form.assigned_crew}
            onChange={(e) => setForm((f) => ({ ...f, assigned_crew: e.target.value }))}
            className={selectCls}
          >
            <option value="">No crew assigned</option>
            {crewsData?.results.map((c) => (
              <option key={c.id} value={c.id}>{c.name} ({c.trade})</option>
            ))}
          </select>
        </Field>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

function CrewModal({ crew, onClose }: { crew?: Crew; onClose: () => void }) {
  const create = useCreateCrew();
  const update = useUpdateCrew();
  const { data: orgMembers = [] } = useOrgMembers();
  const { data: employeesData } = useEmployees({ page_size: '500' });
  const isEdit = !!crew;

  // Build email → hourly rate lookup from the payroll employees list
  const rateByEmail = new Map(
    (employeesData?.results ?? []).map((e) => [e.email, e.base_hourly_rate])
  );

  const [form, setForm] = useState({
    name: crew?.name ?? '',
    trade: crew?.trade ?? '',
    foreman: crew?.foreman ?? '',
    members: crew?.members ?? [] as string[],
    hourly_rate: crew?.hourly_rate ?? '',
    is_active: crew?.is_active ?? true,
  });

  useEffect(() => {
    setForm({
      name: crew?.name ?? '',
      trade: crew?.trade ?? '',
      foreman: crew?.foreman ?? '',
      members: crew?.members ?? [],
      hourly_rate: crew?.hourly_rate ?? '',
      is_active: crew?.is_active ?? true,
    });
  }, [crew]);

  function toggleMember(userId: string) {
    setForm((f) => ({
      ...f,
      members: f.members.includes(userId)
        ? f.members.filter((id) => id !== userId)
        : [...f.members, userId],
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      name: form.name,
      trade: form.trade,
      foreman: form.foreman || null,
      members: form.members,
      hourly_rate: form.hourly_rate || 0,
      is_active: form.is_active,
    };
    if (isEdit) {
      update.mutate({ id: crew.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  const trades = [
    { value: 'general', label: 'General Labor' },
    { value: 'concrete', label: 'Concrete' },
    { value: 'framing', label: 'Framing' },
    { value: 'electrical', label: 'Electrical' },
    { value: 'plumbing', label: 'Plumbing' },
    { value: 'hvac', label: 'HVAC' },
    { value: 'roofing', label: 'Roofing' },
    { value: 'drywall', label: 'Drywall' },
    { value: 'painting', label: 'Painting' },
    { value: 'flooring', label: 'Flooring' },
    { value: 'finish_carpentry', label: 'Finish Carpentry' },
    { value: 'other', label: 'Other' },
  ];

  return (
    <Modal title={isEdit ? 'Edit Crew' : 'New Crew'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Crew Name *">
          <input
            type="text"
            title="Crew Name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className={inputCls}
            placeholder="Crew name…"
          />
        </Field>
        <Field label="Trade *">
          <select
            title="Trade"
            required
            value={form.trade}
            onChange={(e) => setForm((f) => ({ ...f, trade: e.target.value }))}
            className={inputCls}
          >
            <option value="">— Select trade —</option>
            {trades.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </Field>
        <Field label="Foreman">
          <select
            title="Foreman"
            value={form.foreman}
            onChange={(e) => {
              const newForeman = e.target.value;
              setForm((f) => ({
                ...f,
                foreman: newForeman,
                // Remove foreman from members if they were selected
                members: f.members.filter((id) => id !== newForeman),
              }));
            }}
            className={selectCls}
          >
            <option value="">— No foreman assigned —</option>
            {orgMembers.map((m) => (
              <option key={m.user} value={m.user}>{m.user_full_name}</option>
            ))}
          </select>
        </Field>
        <Field label={`Crew Members (${form.members.length} selected)`}>
          <div className="max-h-44 overflow-y-auto rounded-lg border border-slate-200 divide-y divide-slate-50">
            {orgMembers.filter((m) => m.user !== form.foreman).length === 0 && (
              <p className="px-3 py-2 text-sm text-slate-400">No available members.</p>
            )}
            {orgMembers
              .filter((m) => m.user !== form.foreman)
              .map((m) => {
                const checked = form.members.includes(m.user);
                const rate = rateByEmail.get(m.user_email);
                return (
                  <label
                    key={m.user}
                    className="flex cursor-pointer items-center gap-3 px-3 py-2.5 hover:bg-slate-50"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleMember(m.user)}
                      className="h-4 w-4 flex-shrink-0 rounded border-slate-300 accent-amber-500"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-800">{m.user_full_name}</p>
                      <p className="text-xs text-slate-400">{m.user_email}</p>
                    </div>
                    {rate && (
                      <span className="flex-shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                        ${parseFloat(rate).toFixed(2)}/hr
                      </span>
                    )}
                  </label>
                );
              })}
          </div>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Hourly Rate ($)">
            <input
              type="number"
              title="Hourly Rate"
              step="0.01"
              value={form.hourly_rate}
              onChange={(e) => setForm((f) => ({ ...f, hourly_rate: e.target.value }))}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
          <Field label="Status">
            <select
              title="Status"
              value={form.is_active ? 'active' : 'inactive'}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.value === 'active' }))}
              className={selectCls}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </Field>
        </div>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

function EquipmentModal({ equipment, onClose }: { equipment?: Equipment; onClose: () => void }) {
  const create = useCreateEquipment();
  const update = useUpdateEquipment();
  const isEdit = !!equipment;

  const [form, setForm] = useState({
    name: equipment?.name ?? '',
    equipment_type: equipment?.equipment_type ?? '',
    make: equipment?.make ?? '',
    model: equipment?.model ?? '',
    year: equipment?.year ? String(equipment.year) : '',
    daily_rate: equipment?.daily_rate ?? '',
    purchase_price: equipment?.purchase_price ?? '',
    is_available: equipment?.is_available ?? true,
  });

  useEffect(() => {
    setForm({
      name: equipment?.name ?? '',
      equipment_type: equipment?.equipment_type ?? '',
      make: equipment?.make ?? '',
      model: equipment?.model ?? '',
      year: equipment?.year ? String(equipment.year) : '',
      daily_rate: equipment?.daily_rate ?? '',
      purchase_price: equipment?.purchase_price ?? '',
      is_available: equipment?.is_available ?? true,
    });
  }, [equipment]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      name: form.name,
      equipment_type: form.equipment_type,
      make: form.make || '',
      model: form.model || '',
      year: form.year ? parseInt(form.year) : null,
      daily_rental_rate: form.daily_rate || 0,
      purchase_cost: form.purchase_price || null,
      status: form.is_available ? 'available' : 'in_use',
    };
    if (isEdit) {
      update.mutate({ id: equipment.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  const eqTypes = ['Heavy Equipment', 'Light Equipment', 'Tools', 'Vehicles', 'Scaffolding', 'Formwork', 'Other'];

  return (
    <Modal title={isEdit ? 'Edit Equipment' : 'New Equipment'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name *">
          <input
            type="text"
            title="Equipment Name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className={inputCls}
            placeholder="Equipment name…"
          />
        </Field>
        <Field label="Type *">
          <input
            type="text"
            title="Equipment Type"
            required
            list="eq-types-list"
            value={form.equipment_type}
            onChange={(e) => setForm((f) => ({ ...f, equipment_type: e.target.value }))}
            className={inputCls}
            placeholder="Equipment type…"
          />
          <datalist id="eq-types-list">
            {eqTypes.map((t) => <option key={t} value={t} />)}
          </datalist>
        </Field>
        <div className="grid grid-cols-3 gap-3">
          <Field label="Year">
            <input
              type="number"
              title="Year"
              value={form.year}
              onChange={(e) => setForm((f) => ({ ...f, year: e.target.value }))}
              className={inputCls}
              placeholder="2020"
            />
          </Field>
          <Field label="Make">
            <input
              type="text"
              title="Make"
              value={form.make}
              onChange={(e) => setForm((f) => ({ ...f, make: e.target.value }))}
              className={inputCls}
              placeholder="Caterpillar…"
            />
          </Field>
          <Field label="Model">
            <input
              type="text"
              title="Model"
              value={form.model}
              onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))}
              className={inputCls}
              placeholder="320…"
            />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Daily Rate ($)">
            <input
              type="number"
              title="Daily Rate"
              step="0.01"
              value={form.daily_rate}
              onChange={(e) => setForm((f) => ({ ...f, daily_rate: e.target.value }))}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
          <Field label="Purchase Price ($)">
            <input
              type="number"
              title="Purchase Price"
              step="0.01"
              value={form.purchase_price}
              onChange={(e) => setForm((f) => ({ ...f, purchase_price: e.target.value }))}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
        </div>
        <Field label="Availability">
          <select
            title="Availability"
            value={form.is_available ? 'available' : 'in_use'}
            onChange={(e) => setForm((f) => ({ ...f, is_available: e.target.value === 'available' }))}
            className={selectCls}
          >
            <option value="available">Available</option>
            <option value="in_use">In Use</option>
          </select>
        </Field>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

// ─── Shared UI ───────────────────────────────────────────────────────────────

function RowActions({ onEdit, onDelete }: { onEdit: () => void; onDelete: () => void }) {
  return (
    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
      <button
        type="button"
        title="Edit"
        onClick={onEdit}
        className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      </button>
      <button
        type="button"
        title="Delete"
        onClick={onDelete}
        className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-500"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  );
}

const btnCls = 'flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 transition-colors';
const inputCls = 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400';
const selectCls = inputCls + ' bg-white';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      {children}
    </div>
  );
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button
            type="button"
            title="Close"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}

function ModalActions({ onClose, isPending, isEdit }: { onClose: () => void; isPending: boolean; isEdit: boolean }) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button
        type="button"
        onClick={onClose}
        className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={isPending}
        className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
      >
        {isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create'}
      </button>
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
