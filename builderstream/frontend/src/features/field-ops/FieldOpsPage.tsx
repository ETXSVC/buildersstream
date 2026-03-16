/**
 * Desktop Field Ops management view — time entries, daily logs, expenses.
 */
import { useState, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useOpenTimeEntry,
  useTimeEntries, useCreateManualEntry, useApproveTimeEntry, useRejectTimeEntry,
  useDailyLogs, useCreateDailyLog, useSubmitDailyLog, useApproveDailyLog,
  useExpenses, useCreateExpense, useApproveExpense, useRejectExpense,
} from '@/hooks/useFieldOps';
import { useProjects } from '@/hooks/useProjects';
import { EXPENSE_CATEGORIES } from '@/types/field-ops';
import type { TimeEntry, DailyLog, ExpenseEntry } from '@/types/field-ops';

type Tab = 'time-entries' | 'daily-logs' | 'expenses';

function FieldOpsDashboard() {
  const { data: timeData } = useTimeEntries({ page_size: '100' });
  const { data: logsData } = useDailyLogs({ page_size: '100' });
  const { data: expData } = useExpenses({ page_size: '100' });

  const stats = useMemo(() => {
    const entries = timeData?.results ?? [];
    const logs = logsData?.results ?? [];
    const expenses = expData?.results ?? [];
    const totalHours = entries.reduce((s, e) => s + parseFloat(e.total_hours ?? '0'), 0);
    const pendingExpenses = expenses.filter(e => e.status === 'pending').length;
    const expenseTotal = expenses.reduce((s, e) => s + parseFloat(e.amount ?? '0'), 0);
    const statusCounts = logs.reduce<Record<string, number>>((acc, l) => {
      acc[l.status] = (acc[l.status] ?? 0) + 1;
      return acc;
    }, {});
    return { totalHours, pendingExpenses, expenseTotal, logCount: logs.length, statusCounts, entryCount: entries.length };
  }, [timeData, logsData, expData]);

  const logStatusData = Object.entries(stats.statusCounts).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
  }));

  return (
    <div className="mb-2">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Time Entries" value={stats.entryCount} icon="⏱️" />
        <KpiCard label="Total Hours" value={stats.totalHours.toFixed(1)} icon="🕐" accent="blue" />
        <KpiCard label="Daily Logs" value={stats.logCount} icon="📝" accent="indigo" />
        <KpiCard label="Pending Expenses" value={stats.pendingExpenses} icon="💸" accent={stats.pendingExpenses > 0 ? 'amber' : 'default'} sub={`$${(stats.expenseTotal / 1000).toFixed(1)}k total`} />
      </div>
      {logStatusData.length > 0 && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 mb-6">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Daily Logs by Status</h3>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={logStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65}>
                  {logStatusData.map((_, i) => <Cell key={i} fill={['#60a5fa','#22c55e','#f59e0b','#94a3b8'][i % 4]} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Log Status Counts</h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={logStatusData} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export const FieldOpsPage = () => {
  const [tab, setTab] = useState<Tab>('time-entries');
  const [manualModal, setManualModal] = useState(false);
  const [logModal, setLogModal] = useState(false);
  const [expenseModal, setExpenseModal] = useState(false);
  const { data: openEntry } = useOpenTimeEntry();

  const tabs: { key: Tab; label: string }[] = [
    { key: 'time-entries', label: 'Time Entries' },
    { key: 'daily-logs', label: 'Daily Logs' },
    { key: 'expenses', label: 'Expenses' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Field Operations</h1>
        <div>
          {tab === 'time-entries' && (
            <button
              type="button"
              onClick={() => setManualModal(true)}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-600"
            >
              + Manual Entry
            </button>
          )}
          {tab === 'daily-logs' && (
            <button
              type="button"
              onClick={() => setLogModal(true)}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-600"
            >
              + New Log
            </button>
          )}
          {tab === 'expenses' && (
            <button
              type="button"
              onClick={() => setExpenseModal(true)}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-600"
            >
              + New Expense
            </button>
          )}
        </div>
      </div>

      <FieldOpsDashboard />

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
              {openEntry.project_name ? ` · ${openEntry.project_name}` : ''}
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

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
              tab === t.key ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'time-entries' && <TimeEntriesTable />}
      {tab === 'daily-logs' && <DailyLogsTable />}
      {tab === 'expenses' && <ExpensesTable />}

      {manualModal && <ManualEntryModal onClose={() => setManualModal(false)} />}
      {logModal && <DailyLogModal onClose={() => setLogModal(false)} />}
      {expenseModal && <ExpenseModal onClose={() => setExpenseModal(false)} />}
    </div>
  );
};

/* ─── Time Entries Table ─────────────────────────────────────── */
function TimeEntriesTable() {
  const { data, isLoading } = useTimeEntries({ page_size: '20' });
  const approve = useApproveTimeEntry();
  const reject = useRejectTimeEntry();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Employee</Th>
            <Th>Project</Th>
            <Th>Date</Th>
            <Th>Clock In</Th>
            <Th>Clock Out</Th>
            <Th>Hours</Th>
            <Th>Type</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No time entries found.</td></tr>
          )}
          {data?.results.map((entry) => (
            <tr key={entry.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{entry.employee_name}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{entry.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {new Date(entry.clock_in).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {new Date(entry.clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {entry.clock_out
                  ? new Date(entry.clock_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  : <span className="text-green-600 font-medium">Active</span>}
              </td>
              <td className="px-4 py-3 font-semibold text-slate-900">
                {entry.total_hours ? `${Number(entry.total_hours).toFixed(1)}h` : '—'}
                {Number(entry.overtime_hours) > 0 && (
                  <span className="ml-1 text-xs text-amber-600">+{Number(entry.overtime_hours).toFixed(1)}OT</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600 capitalize">
                  {entry.entry_type}
                </span>
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={entry.status} />
              </td>
              <td className="px-4 py-3">
                {entry.status === 'pending' && (
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ActionBtn onClick={() => approve.mutate(entry.id)}>Approve</ActionBtn>
                    <ActionBtn danger onClick={() => reject.mutate(entry.id)}>Reject</ActionBtn>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="entries" />
    </div>
  );
}

/* ─── Daily Logs Table ───────────────────────────────────────── */
function DailyLogsTable() {
  const { data, isLoading } = useDailyLogs({ page_size: '20' });
  const submit = useSubmitDailyLog();
  const approve = useApproveDailyLog();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Project</Th>
            <Th>Date</Th>
            <Th>Created By</Th>
            <Th>Manpower</Th>
            <Th>Work Performed</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No daily logs found.</td></tr>
          )}
          {data?.results.map((log) => (
            <tr key={log.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{log.project_name}</td>
              <td className="px-4 py-3 text-slate-600">{fmtDate(log.log_date)}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{log.created_by_name}</td>
              <td className="px-4 py-3 text-center text-slate-700">{log.manpower_count}</td>
              <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{log.work_performed || '—'}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  log.status === 'approved' ? 'bg-green-100 text-green-700'
                  : log.status === 'submitted' ? 'bg-amber-100 text-amber-700'
                  : 'bg-slate-100 text-slate-600'
                }`}>
                  {log.status}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {log.status === 'draft' && (
                    <ActionBtn onClick={() => submit.mutate(log.id)}>Submit</ActionBtn>
                  )}
                  {log.status === 'submitted' && (
                    <ActionBtn onClick={() => approve.mutate(log.id)}>Approve</ActionBtn>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="logs" />
    </div>
  );
}

/* ─── Expenses Table ─────────────────────────────────────────── */
function ExpensesTable() {
  const { data, isLoading } = useExpenses({ page_size: '20' });
  const approve = useApproveExpense();
  const reject = useRejectExpense();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Employee</Th>
            <Th>Project</Th>
            <Th>Date</Th>
            <Th>Category</Th>
            <Th>Description</Th>
            <Th>Amount</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No expenses found.</td></tr>
          )}
          {data?.results.map((exp) => (
            <tr key={exp.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{exp.employee_name}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{exp.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{fmtDate(exp.incurred_date)}</td>
              <td className="px-4 py-3 text-slate-600">{EXPENSE_CATEGORIES[exp.category] ?? exp.category}</td>
              <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{exp.description}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">
                ${Number(exp.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={exp.status} />
              </td>
              <td className="px-4 py-3">
                {exp.status === 'pending' && (
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ActionBtn onClick={() => approve.mutate(exp.id)}>Approve</ActionBtn>
                    <ActionBtn danger onClick={() => reject.mutate(exp.id)}>Reject</ActionBtn>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="expenses" />
    </div>
  );
}

/* ─── Manual Time Entry Modal ────────────────────────────────── */
function ManualEntryModal({ onClose }: { onClose: () => void }) {
  const create = useCreateManualEntry();
  const { data: projects } = useProjects({ page_size: '100' });
  const [form, setForm] = useState({
    project: '',
    clock_in: '',
    clock_out: '',
    notes: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      clock_in: form.clock_in,
      entry_type: 'manual',
    };
    if (form.project) payload.project = form.project;
    if (form.clock_out) payload.clock_out = form.clock_out;
    if (form.notes) payload.notes = form.notes;
    create.mutate(payload, { onSuccess: onClose });
  }

  return (
    <Modal title="Manual Time Entry" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Project">
          <select
            title="Project"
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            className={selectCls}
          >
            <option value="">— Select project —</option>
            {projects?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Clock In *">
            <input
              title="Clock in time"
              type="datetime-local"
              required
              value={form.clock_in}
              onChange={(e) => setForm({ ...form, clock_in: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Clock Out">
            <input
              title="Clock out time"
              type="datetime-local"
              value={form.clock_out}
              onChange={(e) => setForm({ ...form, clock_out: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Notes">
          <textarea
            title="Notes"
            rows={2}
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Optional notes"
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} busy={create.isPending} isEdit={false} />
      </form>
    </Modal>
  );
}

/* ─── Daily Log Modal ────────────────────────────────────────── */
function DailyLogModal({ onClose }: { onClose: () => void }) {
  const create = useCreateDailyLog();
  const { data: projects } = useProjects({ page_size: '100' });
  const [form, setForm] = useState({
    project: '',
    log_date: new Date().toISOString().split('T')[0],
    work_performed: '',
    manpower_count: '0',
    delay_reason: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      log_date: form.log_date,
      work_performed: form.work_performed,
      manpower_count: Number(form.manpower_count),
    };
    if (form.project) payload.project = form.project;
    if (form.delay_reason) payload.delay_reason = form.delay_reason;
    create.mutate(payload, { onSuccess: onClose });
  }

  return (
    <Modal title="New Daily Log" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Project *">
          <select
            title="Project"
            required
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            className={selectCls}
          >
            <option value="">— Select project —</option>
            {projects?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Log Date *">
            <input
              title="Log date"
              type="date"
              required
              value={form.log_date}
              onChange={(e) => setForm({ ...form, log_date: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Manpower Count">
            <input
              title="Manpower count"
              type="number"
              min="0"
              value={form.manpower_count}
              onChange={(e) => setForm({ ...form, manpower_count: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Work Performed *">
          <textarea
            title="Work performed"
            required
            rows={3}
            value={form.work_performed}
            onChange={(e) => setForm({ ...form, work_performed: e.target.value })}
            placeholder="Describe the work completed today"
            className={inputCls}
          />
        </Field>
        <Field label="Delay Reason">
          <select
            title="Delay reason"
            value={form.delay_reason}
            onChange={(e) => setForm({ ...form, delay_reason: e.target.value })}
            className={selectCls}
          >
            <option value="">— None —</option>
            <option value="WEATHER">Weather</option>
            <option value="MATERIAL">Material Shortage</option>
            <option value="EQUIPMENT">Equipment Failure</option>
            <option value="LABOR">Labor Shortage</option>
            <option value="INSPECTION">Inspection / Permit</option>
            <option value="DESIGN">Design Change</option>
            <option value="OWNER">Owner Request</option>
            <option value="OTHER">Other</option>
          </select>
        </Field>
        <ModalActions onClose={onClose} busy={create.isPending} isEdit={false} />
      </form>
    </Modal>
  );
}

/* ─── Expense Modal ──────────────────────────────────────────── */
function ExpenseModal({ onClose }: { onClose: () => void }) {
  const create = useCreateExpense();
  const { data: projects } = useProjects({ page_size: '100' });
  const [form, setForm] = useState({
    project: '',
    category: 'OTHER',
    description: '',
    amount: '',
    incurred_date: new Date().toISOString().split('T')[0],
    mileage: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      category: form.category,
      description: form.description,
      amount: form.amount,
      incurred_date: form.incurred_date,
    };
    if (form.project) payload.project = form.project;
    if (form.mileage) payload.mileage = form.mileage;
    create.mutate(payload, { onSuccess: onClose });
  }

  return (
    <Modal title="New Expense" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Project">
          <select
            title="Project"
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            className={selectCls}
          >
            <option value="">— Select project —</option>
            {projects?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Category *">
            <select
              title="Category"
              required
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className={selectCls}
            >
              {Object.entries(EXPENSE_CATEGORIES).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </Field>
          <Field label="Date *">
            <input
              title="Expense date"
              type="date"
              required
              value={form.incurred_date}
              onChange={(e) => setForm({ ...form, incurred_date: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Description *">
          <input
            title="Description"
            required
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="What was purchased or expensed"
            className={inputCls}
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Amount ($) *">
            <input
              title="Amount"
              type="number"
              step="0.01"
              min="0"
              required
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="0.00"
              className={inputCls}
            />
          </Field>
          {form.category === 'FUEL' && (
            <Field label="Mileage">
              <input
                title="Mileage"
                type="number"
                step="0.1"
                min="0"
                value={form.mileage}
                onChange={(e) => setForm({ ...form, mileage: e.target.value })}
                placeholder="Miles"
                className={inputCls}
              />
            </Field>
          )}
        </div>
        <ModalActions onClose={onClose} busy={create.isPending} isEdit={false} />
      </form>
    </Modal>
  );
}

/* ─── Shared UI Primitives ───────────────────────────────────── */
function StatusBadge({ status }: { status: 'pending' | 'approved' | 'rejected' }) {
  const cls =
    status === 'approved' ? 'bg-green-100 text-green-700'
    : status === 'rejected' ? 'bg-red-100 text-red-600'
    : 'bg-slate-100 text-slate-600';
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${cls}`}>{status}</span>
  );
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button type="button" title="Close" onClick={onClose} className="rounded p-1 text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-6 py-4">{children}</div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      {children}
    </div>
  );
}

function ModalActions({ onClose, busy, isEdit }: { onClose: () => void; busy: boolean; isEdit: boolean }) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onClose} className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
        Cancel
      </button>
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
      >
        {busy ? 'Saving…' : isEdit ? 'Save Changes' : 'Create'}
      </button>
    </div>
  );
}

function ActionBtn({ children, onClick, danger }: { children: React.ReactNode; onClick: () => void; danger?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
        danger ? 'text-red-600 hover:bg-red-50' : 'text-amber-700 hover:bg-amber-50'
      }`}
    >
      {children}
    </button>
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

const inputCls = 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400';
const selectCls = 'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400';
