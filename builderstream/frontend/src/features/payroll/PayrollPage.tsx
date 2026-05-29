import { useState, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  usePayRuns, useCreatePayRun, useProcessPayRun, useApprovePayRun, useMarkPayRunPaid, useVoidPayRun,
  useCertifiedPayrolls, useSubmitCertifiedPayroll,
  useWorkforceSummary,
  useEmployees, useCreateEmployee, useUpdateEmployee,
} from '@/hooks/usePayroll';
import { PAY_RUN_STATUS_COLORS, EMPLOYMENT_TYPE_LABELS, EMPLOYMENT_TYPE_COLORS, TRADE_LABELS } from '@/types/payroll';
import type { Employee, EmploymentType, EmployeeTrade, PayRun, PayRunStatus } from '@/types/payroll';

type Tab = 'pay-runs' | 'certified' | 'employees' | 'workforce';

function PayrollDashboard({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const { data: payRunsData } = usePayRuns({});
  const { data: employeesData } = useEmployees({});
  const { data: workforce } = useWorkforceSummary();

  const stats = useMemo(() => {
    const payRuns = payRunsData?.results ?? [];
    const employees = employeesData?.results ?? [];
    const active = employees.filter(e => e.is_active).length;
    const contractors = employees.filter(e => e.employment_type === 'contractor').length;
    const pendingRuns = payRuns.filter(r => r.status === 'draft').length;
    const lastPaid = payRuns.filter(r => r.status === 'paid').sort((a, b) => b.pay_period_end.localeCompare(a.pay_period_end))[0];
    const lastTotal = lastPaid ? parseFloat(lastPaid.total_net_pay ?? '0') : 0;
    const typeCounts = employees.reduce<Record<string, number>>((acc, e) => {
      acc[e.employment_type] = (acc[e.employment_type] ?? 0) + 1;
      return acc;
    }, {});
    const tradeCounts = employees.reduce<Record<string, number>>((acc, e) => {
      if (e.trade) acc[e.trade] = (acc[e.trade] ?? 0) + 1;
      return acc;
    }, {});
    return { active, contractors, pendingRuns, lastTotal, typeCounts, tradeCounts };
  }, [payRunsData, employeesData, workforce]);

  const typeData = Object.entries(stats.typeCounts).map(([k, v]) => ({
    name: EMPLOYMENT_TYPE_LABELS[k as EmploymentType] ?? k,
    value: v,
  }));

  const tradeData = Object.entries(stats.tradeCounts).map(([k, v]) => ({
    name: TRADE_LABELS[k as EmployeeTrade] ?? k,
    value: v,
  }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Active Employees" value={stats.active} icon="👷" accent="blue" onClick={() => onNavigate('employees')} />
        <KpiCard label="Contractors" value={stats.contractors} icon="🤝" onClick={() => onNavigate('workforce')} />
        <KpiCard label="Pending Pay Runs" value={stats.pendingRuns} icon="📊" accent={stats.pendingRuns > 0 ? 'amber' : 'default'} onClick={() => onNavigate('pay-runs')} />
        <KpiCard label="Last Payroll Net" value={stats.lastTotal > 0 ? `$${(stats.lastTotal / 1000).toFixed(1)}k` : '—'} icon="💵" accent={stats.lastTotal > 0 ? 'green' : 'default'} onClick={() => onNavigate('pay-runs')} />
      </div>
      {(typeData.length > 0 || tradeData.length > 0) && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {typeData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Employment Type Mix</h3>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={typeData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65}>
                    {typeData.map((_, i) => <Cell key={i} fill={['#60a5fa','#f59e0b','#22c55e','#94a3b8'][i % 4]} />)}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          {tradeData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Workforce by Trade</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={tradeData} margin={{ top: 0, right: 8, left: -20, bottom: 40 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#a78bfa" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const PayrollPage = () => {
  const [tab, setTab] = useState<Tab>('pay-runs');
  const [createModal, setCreateModal] = useState(false);
  const [paidModal, setPaidModal] = useState<PayRun | null>(null);
  const [employeeModal, setEmployeeModal] = useState<Employee | null | 'new'>(null);

  const handleNavigate = (t: Tab) => {
    setTab(t);
    setTimeout(() => document.getElementById('payroll-list')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Payroll & Workforce</h1>
        {tab === 'pay-runs' && (
          <button
            type="button"
            onClick={() => setCreateModal(true)}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-600"
          >
            + New Pay Run
          </button>
        )}
        {tab === 'employees' && (
          <button
            type="button"
            onClick={() => setEmployeeModal('new')}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-600"
          >
            + Add Employee / Contractor
          </button>
        )}
      </div>
      <PayrollDashboard onNavigate={handleNavigate} />

      <div id="payroll-list" className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {([
          { key: 'pay-runs', label: 'Pay Runs' },
          { key: 'certified', label: 'Certified Payroll' },
          { key: 'employees', label: 'Employees & Contractors' },
          { key: 'workforce', label: 'Workforce Summary' },
        ] as { key: Tab; label: string }[]).map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
              tab === key ? 'bg-blue-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'pay-runs' && (
        <PayRunsTable onMarkPaid={(run) => setPaidModal(run)} />
      )}
      {tab === 'certified' && <CertifiedPayrollTable />}
      {tab === 'employees' && <EmployeesTable onEdit={(emp) => setEmployeeModal(emp)} />}
      {tab === 'workforce' && <WorkforcePanel />}

      {createModal && <CreatePayRunModal onClose={() => setCreateModal(false)} />}
      {paidModal && (
        <MarkPaidModal run={paidModal} onClose={() => setPaidModal(null)} />
      )}
      {employeeModal !== null && (
        <EmployeeModal
          employee={employeeModal === 'new' ? null : employeeModal}
          onClose={() => setEmployeeModal(null)}
        />
      )}
    </div>
  );
};

/* ─── Pay Runs Table ─────────────────────────────────────────── */
function PayRunsTable({ onMarkPaid }: { onMarkPaid: (run: PayRun) => void }) {
  const { data, isLoading } = usePayRuns({ page_size: '20' });
  const process = useProcessPayRun();
  const approve = useApprovePayRun();
  const void_ = useVoidPayRun();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Pay Period</Th>
            <Th>Workers</Th>
            <Th>Regular Hours</Th>
            <Th>OT Hours</Th>
            <Th>Gross Pay</Th>
            <Th>Net Pay</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No pay runs found.</td></tr>
          )}
          {data?.results.map((run) => {
            const otHours = parseFloat(run.total_overtime_hours);
            const regHours = parseFloat(run.total_regular_hours);
            return (
              <tr key={run.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">
                  {fmtDate(run.pay_period_start)} –{' '}
                  {fmtDate(run.pay_period_end)}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">{run.employee_count}</td>
                <td className="px-4 py-3 text-slate-700">{regHours.toFixed(1)} h</td>
                <td className="px-4 py-3 text-slate-700">
                  {otHours > 0 ? (
                    <span className="text-blue-600 font-medium">{otHours.toFixed(1)} h</span>
                  ) : (
                    <span className="text-slate-400">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-slate-900">{fmt(run.total_gross_pay)}</td>
                <td className="px-4 py-3 font-semibold text-slate-900">{fmt(run.total_net_pay)}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PAY_RUN_STATUS_COLORS[run.status]}`}>
                    {run.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <PayRunActions
                    run={run}
                    onProcess={() => process.mutate(run.id)}
                    onApprove={() => approve.mutate(run.id)}
                    onMarkPaid={() => onMarkPaid(run)}
                    onVoid={() => {
                      if (confirm(`Void pay run for ${fmtDate(run.pay_period_start)} – ${fmtDate(run.pay_period_end)}? This cannot be undone.`)) {
                        void_.mutate(run.id);
                      }
                    }}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="pay runs" />
    </div>
  );
}

function PayRunActions({
  run,
  onProcess,
  onApprove,
  onMarkPaid,
  onVoid,
}: {
  run: PayRun;
  onProcess: () => void;
  onApprove: () => void;
  onMarkPaid: () => void;
  onVoid: () => void;
}) {
  if (run.status === 'paid' || run.status === 'voided') return null;
  return (
    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
      {run.status === 'draft' && (
        <ActionBtn onClick={onProcess}>Process</ActionBtn>
      )}
      {run.status === 'processing' && (
        <ActionBtn onClick={onApprove}>Approve</ActionBtn>
      )}
      {run.status === 'approved' && (
        <ActionBtn onClick={onMarkPaid}>Mark Paid</ActionBtn>
      )}
      {run.status !== 'draft' && (
        <ActionBtn danger onClick={onVoid}>Void</ActionBtn>
      )}
    </div>
  );
}

/* ─── Create Pay Run Modal ───────────────────────────────────── */
function CreatePayRunModal({ onClose }: { onClose: () => void }) {
  const create = useCreatePayRun();
  const today = new Date().toISOString().split('T')[0];

  // Default to previous two-week pay period
  const defaultEnd = today;
  const defaultStart = (() => {
    const d = new Date();
    d.setDate(d.getDate() - 13);
    return d.toISOString().split('T')[0];
  })();

  const [form, setForm] = useState({
    pay_period_start: defaultStart,
    pay_period_end: defaultEnd,
    pay_date: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      pay_period_start: form.pay_period_start,
      pay_period_end: form.pay_period_end,
    };
    if (form.pay_date) payload.pay_date = form.pay_date;
    create.mutate(payload, { onSuccess: onClose });
  }

  return (
    <Modal title="New Pay Run" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="rounded-lg bg-blue-50 border border-blue-100 px-4 py-3 text-xs text-blue-700">
          Creating a pay run will calculate wages for all approved time entries in the selected period.
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Period Start *">
            <input
              title="Pay period start"
              type="date"
              required
              value={form.pay_period_start}
              onChange={(e) => setForm({ ...form, pay_period_start: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Period End *">
            <input
              title="Pay period end"
              type="date"
              required
              value={form.pay_period_end}
              onChange={(e) => setForm({ ...form, pay_period_end: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Pay Date">
          <input
            title="Pay date"
            type="date"
            value={form.pay_date}
            onChange={(e) => setForm({ ...form, pay_date: e.target.value })}
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} busy={create.isPending} submitLabel="Create Pay Run" />
      </form>
    </Modal>
  );
}

/* ─── Mark Paid Modal ────────────────────────────────────────── */
function MarkPaidModal({ run, onClose }: { run: PayRun; onClose: () => void }) {
  const markPaid = useMarkPayRunPaid();
  const [payDate, setPayDate] = useState(new Date().toISOString().split('T')[0]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    markPaid.mutate({ id: run.id, payDate }, { onSuccess: onClose });
  }

  return (
    <Modal title="Mark Pay Run as Paid" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-sm text-slate-600">
          Confirm payment for period{' '}
          <span className="font-medium text-slate-900">
            {fmtDate(run.pay_period_start)} – {fmtDate(run.pay_period_end)}
          </span>
          {'. '}
          Net pay: <span className="font-semibold text-slate-900">{fmt(run.total_net_pay)}</span>
        </p>
        <Field label="Payment Date *">
          <input
            title="Payment date"
            type="date"
            required
            value={payDate}
            onChange={(e) => setPayDate(e.target.value)}
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} busy={markPaid.isPending} submitLabel="Confirm Payment" />
      </form>
    </Modal>
  );
}

/* ─── Certified Payroll Table ────────────────────────────────── */
function CertifiedPayrollTable() {
  const { data, isLoading } = useCertifiedPayrolls({ page_size: '20' });
  const submit = useSubmitCertifiedPayroll();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Project</Th>
            <Th>Week Ending</Th>
            <Th>Week #</Th>
            <Th>Contractor</Th>
            <Th>Workers</Th>
            <Th>Total Wages</Th>
            <Th>Submitted</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No certified payroll reports found.</td></tr>
          )}
          {data?.results.map((cp) => (
            <tr key={cp.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 text-slate-900">{cp.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700">{fmtDate(cp.pay_period_end)}</td>
              <td className="px-4 py-3 text-center text-slate-500">{cp.week_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{cp.contractor_name}</td>
              <td className="px-4 py-3 text-center text-slate-700">{cp.worker_count}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">{fmt(cp.total_wages)}</td>
              <td className="px-4 py-3">
                {cp.submitted ? (
                  <span className="text-xs font-medium text-green-600">
                    ✓ {cp.submitted_date ? fmtDate(cp.submitted_date) : 'Submitted'}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400">Pending</span>
                )}
              </td>
              <td className="px-4 py-3">
                {!cp.submitted && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <ActionBtn
                      onClick={() => {
                        if (confirm('Submit this certified payroll report?')) submit.mutate(cp.id);
                      }}
                    >
                      Submit
                    </ActionBtn>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="reports" />
    </div>
  );
}

/* ─── Workforce Panel ────────────────────────────────────────── */
function WorkforcePanel() {
  const { data, isLoading } = useWorkforceSummary();
  if (isLoading) return <Spinner />;
  if (!data) return <div className="text-slate-400 text-sm p-4">No workforce data available.</div>;

  const stats = [
    { label: 'Total Workers', value: String(data.total_workers), color: 'text-slate-900' },
    { label: 'Active This Week', value: String(data.active_this_week), color: 'text-green-600' },
    { label: 'Total Hours (wk)', value: data.total_hours_this_week.toFixed(0), color: 'text-slate-900' },
    { label: 'Overtime Hours (wk)', value: data.overtime_hours_this_week.toFixed(0), color: data.overtime_hours_this_week > 0 ? 'text-blue-600' : 'text-slate-400' },
    { label: 'Avg Hourly Rate', value: data.avg_hourly_rate != null ? `$${data.avg_hourly_rate.toFixed(2)}` : '—', color: 'text-slate-900' },
    { label: 'Labor Cost (wk)', value: fmt(data.labor_cost_this_week), color: 'text-slate-900' },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
      {stats.map((s) => (
        <div key={s.label} className="rounded-xl border border-slate-200 bg-white p-4">
          <p className="text-xs text-slate-500 mb-1">{s.label}</p>
          <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
        </div>
      ))}
    </div>
  );
}

/* ─── Employees & Contractors Table ─────────────────────────── */
function EmployeesTable({ onEdit }: { onEdit: (emp: Employee) => void }) {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const { data, isLoading } = useEmployees(
    Object.fromEntries(
      Object.entries({ search, employment_type: typeFilter }).filter(([, v]) => v !== '')
    )
  );

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-400 w-64"
        />
        <select
          title="Filter by employment type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">All Types</option>
          <option value="w2_full_time">W-2 Full Time</option>
          <option value="w2_part_time">W-2 Part Time</option>
          <option value="1099_contractor">1099 Contractor</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <Th>Name</Th>
              <Th>Type</Th>
              <Th>Trade</Th>
              <Th>Hourly Rate</Th>
              <Th>Hire Date</Th>
              <Th>Status</Th>
              <Th></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                  No employees or contractors found.
                </td>
              </tr>
            )}
            {data?.results.map((emp) => (
              <tr key={emp.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3">
                  <div className="font-medium text-slate-900">{emp.full_name}</div>
                  {emp.email && <div className="text-xs text-slate-400">{emp.email}</div>}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${EMPLOYMENT_TYPE_COLORS[emp.employment_type]}`}>
                    {EMPLOYMENT_TYPE_LABELS[emp.employment_type]}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600 capitalize">
                  {TRADE_LABELS[emp.trade] ?? emp.trade}
                </td>
                <td className="px-4 py-3 text-slate-900">
                  ${parseFloat(emp.base_hourly_rate).toFixed(2)}/hr
                </td>
                <td className="px-4 py-3 text-slate-500">
                  {fmtDate(emp.hire_date)}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${emp.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                    {emp.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <ActionBtn onClick={() => onEdit(emp)}>Edit</ActionBtn>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="employees" />
      </div>
    </div>
  );
}

/* ─── Employee Modal (Add / Edit) ────────────────────────────── */
const TRADES: { value: EmployeeTrade; label: string }[] = [
  { value: 'general', label: 'General' },
  { value: 'framing', label: 'Framing' },
  { value: 'electrical', label: 'Electrical' },
  { value: 'plumbing', label: 'Plumbing' },
  { value: 'hvac', label: 'HVAC' },
  { value: 'painting', label: 'Painting' },
  { value: 'flooring', label: 'Flooring' },
  { value: 'roofing', label: 'Roofing' },
  { value: 'concrete', label: 'Concrete' },
  { value: 'drywall', label: 'Drywall' },
  { value: 'finish_carpentry', label: 'Finish Carpentry' },
  { value: 'other', label: 'Other' },
];

function EmployeeModal({ employee, onClose }: { employee: Employee | null; onClose: () => void }) {
  const create = useCreateEmployee();
  const update = useUpdateEmployee();
  const isEdit = employee !== null;

  const [form, setForm] = useState({
    first_name: employee?.first_name ?? '',
    last_name: employee?.last_name ?? '',
    email: employee?.email ?? '',
    phone: employee?.phone ?? '',
    employment_type: (employee?.employment_type ?? 'w2_full_time') as EmploymentType,
    trade: (employee?.trade ?? 'general') as EmployeeTrade,
    hire_date: employee?.hire_date ?? new Date().toISOString().split('T')[0],
    base_hourly_rate: employee?.base_hourly_rate ?? '',
    is_active: employee?.is_active ?? true,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      ...form,
      base_hourly_rate: parseFloat(form.base_hourly_rate) || 0,
    };
    if (isEdit) {
      update.mutate({ id: employee.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Employee / Contractor' : 'Add Employee / Contractor'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="First Name *">
            <input
              title="First name"
              type="text"
              required
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Last Name *">
            <input
              title="Last name"
              type="text"
              required
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Email">
            <input
              title="Email"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Phone">
            <input
              title="Phone"
              type="tel"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Employment Type *">
            <select
              title="Employment type"
              required
              value={form.employment_type}
              onChange={(e) => setForm({ ...form, employment_type: e.target.value as EmploymentType })}
              className={inputCls}
            >
              <option value="w2_full_time">W-2 Full Time</option>
              <option value="w2_part_time">W-2 Part Time</option>
              <option value="1099_contractor">1099 Contractor</option>
            </select>
          </Field>
          <Field label="Trade *">
            <select
              title="Trade"
              required
              value={form.trade}
              onChange={(e) => setForm({ ...form, trade: e.target.value as EmployeeTrade })}
              className={inputCls}
            >
              {TRADES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Hire Date *">
            <input
              title="Hire date"
              type="date"
              required
              value={form.hire_date}
              onChange={(e) => setForm({ ...form, hire_date: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Base Hourly Rate ($) *">
            <input
              title="Base hourly rate"
              type="number"
              required
              min="0"
              step="0.01"
              value={form.base_hourly_rate}
              onChange={(e) => setForm({ ...form, base_hourly_rate: e.target.value })}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
        </div>
        {isEdit && (
          <Field label="Status">
            <select
              title="Status"
              value={form.is_active ? 'active' : 'inactive'}
              onChange={(e) => setForm({ ...form, is_active: e.target.value === 'active' })}
              className={inputCls}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </Field>
        )}
        <ModalActions onClose={onClose} busy={busy} submitLabel={isEdit ? 'Save Changes' : 'Add Employee'} />
      </form>
    </Modal>
  );
}

/* ─── Shared UI Primitives ───────────────────────────────────── */
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

function ModalActions({ onClose, busy, submitLabel }: { onClose: () => void; busy: boolean; submitLabel?: string }) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onClose} className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
        Cancel
      </button>
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-50"
      >
        {busy ? 'Saving…' : (submitLabel ?? 'Create')}
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
        danger ? 'text-red-600 hover:bg-red-50' : 'text-blue-700 hover:bg-blue-50'
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
      <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
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

function fmt(val: number | string | null | undefined) {
  if (val == null) return '—';
  const n = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(n)) return '—';
  return `$${n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

const inputCls = 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400';
