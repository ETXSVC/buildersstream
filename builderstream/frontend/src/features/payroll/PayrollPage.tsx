import { useState } from 'react';
import { usePayRuns, useCertifiedPayrolls, useWorkforceSummary } from '@/hooks/usePayroll';
import { PAY_RUN_STATUS_COLORS } from '@/types/payroll';

type Tab = 'pay-runs' | 'certified' | 'workforce';

export const PayrollPage = () => {
  const [tab, setTab] = useState<Tab>('pay-runs');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Payroll & Workforce</h1>
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {([
          { key: 'pay-runs', label: 'Pay Runs' },
          { key: 'certified', label: 'Certified Payroll' },
          { key: 'workforce', label: 'Workforce' },
        ] as { key: Tab; label: string }[]).map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
              tab === key ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'pay-runs' && <PayRunsTable />}
      {tab === 'certified' && <CertifiedPayrollTable />}
      {tab === 'workforce' && <WorkforcePanel />}
    </div>
  );
};

function PayRunsTable() {
  const { data, isLoading } = usePayRuns({ page_size: '20' });
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
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No pay runs found.</td></tr>
          )}
          {data?.results.map((run) => {
            const otHours = parseFloat(run.total_overtime_hours);
            const regHours = parseFloat(run.total_regular_hours);
            return (
              <tr key={run.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">
                  {new Date(run.pay_period_start).toLocaleDateString()} –{' '}
                  {new Date(run.pay_period_end).toLocaleDateString()}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">{run.employee_count}</td>
                <td className="px-4 py-3 text-slate-700">{regHours.toFixed(1)} h</td>
                <td className="px-4 py-3 text-slate-700">
                  {otHours > 0 ? (
                    <span className="text-amber-600 font-medium">{otHours.toFixed(1)} h</span>
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
              </tr>
            );
          })}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="pay runs" />
    </div>
  );
}

function CertifiedPayrollTable() {
  const { data, isLoading } = useCertifiedPayrolls({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Project</Th>
            <Th>Week Ending</Th>
            <Th>Contractor</Th>
            <Th>Workers</Th>
            <Th>Total Wages</Th>
            <Th>Submitted</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No certified payroll reports found.</td></tr>
          )}
          {data?.results.map((cp) => (
            <tr key={cp.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 text-slate-900">{cp.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700">{new Date(cp.pay_period_end).toLocaleDateString()}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{cp.contractor_name}</td>
              <td className="px-4 py-3 text-center text-slate-700">{cp.worker_count}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">{fmt(cp.total_wages)}</td>
              <td className="px-4 py-3">
                {cp.submitted ? (
                  <span className="text-xs font-medium text-green-600">
                    ✓ {cp.submitted_date ? new Date(cp.submitted_date).toLocaleDateString() : 'Submitted'}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400">Pending</span>
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

function WorkforcePanel() {
  const { data, isLoading } = useWorkforceSummary();
  if (isLoading) return <Spinner />;
  if (!data) return <div className="text-slate-400 text-sm p-4">No workforce data available.</div>;

  const stats = [
    { label: 'Total Workers', value: String(data.total_workers), color: 'text-slate-900' },
    { label: 'Active This Week', value: String(data.active_this_week), color: 'text-green-600' },
    { label: 'Total Hours (wk)', value: data.total_hours_this_week.toFixed(0), color: 'text-slate-900' },
    { label: 'Overtime Hours (wk)', value: data.overtime_hours_this_week.toFixed(0), color: data.overtime_hours_this_week > 0 ? 'text-amber-600' : 'text-slate-400' },
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

function fmt(val: number | string | null | undefined) {
  if (val == null) return '—';
  const n = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(n)) return '—';
  return `$${n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
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
