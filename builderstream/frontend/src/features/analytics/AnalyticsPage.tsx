import { useReports } from '@/hooks/useAnalytics';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { REPORT_TYPE_LABELS } from '@/types/analytics';
import { KpiCard } from '@/components/KpiCard';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, CartesianGrid,
} from 'recharts';

interface OrgSummary {
  financial: {
    revenue_mtd: number;
    expenses_mtd: number;
    gross_profit_mtd: number;
    overdue_invoices_count: number;
    overdue_invoices_amount: number;
    total_budgeted: number;
    total_actual_cost: number;
    budget_variance: number;
  };
  projects: {
    total_projects: number;
    active_projects: number;
    status_breakdown: Record<string, number>;
    health_green: number;
    health_yellow: number;
    health_red: number;
  };
  labor: {
    total_hours_mtd: number;
    overtime_hours_mtd: number;
    overtime_rate: number;
  };
  safety: {
    total_incidents: number;
    recordable_incidents: number;
    lost_time_incidents: number;
  };
  service: {
    open_tickets: number;
    active_warranties: number;
  };
}

interface ForecastMonth {
  month: string;
  inflows?: number;
  outflows?: number;
  net?: number;
  expected_revenue?: number;
}

interface ForecastData {
  forecast_months: number;
  generated_at: string;
  cash_flow: ForecastMonth[];
  pipeline: ForecastMonth[];
}

function useForecast(months = 6) {
  return useQuery<ForecastData>({
    queryKey: ['analytics', 'forecast', months],
    queryFn: async () => {
      const { data } = await apiClient.get<ForecastData>(`/api/v1/analytics/forecast/?months=${months}`);
      return data;
    },
    staleTime: 300_000,
  });
}

function useOrgSummary() {
  return useQuery<OrgSummary>({
    queryKey: ['analytics', 'summary'],
    queryFn: async () => {
      const { data } = await apiClient.get<OrgSummary>('/api/v1/analytics/summary/');
      return data;
    },
    staleTime: 60_000,
  });
}

function fmtCurrency(val: number) {
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}k`;
  return `$${val.toLocaleString()}`;
}

export const AnalyticsPage = () => {
  const { data: summary, isLoading, error } = useOrgSummary();
  const { data: reports } = useReports({ page_size: '20' });
  const { data: forecast } = useForecast(6);

  const f = summary?.financial;
  const p = summary?.projects;
  const l = summary?.labor;
  const s = summary?.safety;
  const svc = summary?.service;

  const healthData = p ? [
    { name: 'Green', value: p.health_green, color: '#22c55e' },
    { name: 'Yellow', value: p.health_yellow, color: '#f59e0b' },
    { name: 'Red', value: p.health_red, color: '#ef4444' },
  ].filter(d => d.value > 0) : [];

  const statusData = p
    ? Object.entries(p.status_breakdown).map(([k, v]) => ({ name: k.replace('_', ' '), value: v }))
    : [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load analytics summary.
        </div>
      )}

      {summary && (
        <>
          {/* Financial */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-slate-700">Financial — Month to Date</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <KpiCard label="Revenue MTD" value={fmtCurrency(f!.revenue_mtd)} icon="💰" accent="green" />
              <KpiCard label="Expenses MTD" value={fmtCurrency(f!.expenses_mtd)} icon="💳" />
              <KpiCard label="Gross Profit" value={fmtCurrency(f!.gross_profit_mtd)} icon="📈"
                accent={f!.gross_profit_mtd >= 0 ? 'green' : 'red'} />
              <KpiCard label="Overdue Invoices" value={f!.overdue_invoices_count} icon="⚠️"
                accent={f!.overdue_invoices_count > 0 ? 'red' : 'default'}
                sub={f!.overdue_invoices_count > 0 ? fmtCurrency(f!.overdue_invoices_amount) : 'None overdue'} />
            </div>
          </section>

          {/* Projects */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-slate-700">Projects</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-4">
              <KpiCard label="Total Projects" value={p!.total_projects} icon="🏗️" />
              <KpiCard label="Active" value={p!.active_projects} icon="⚡" accent="blue" />
              <KpiCard label="Health Green" value={p!.health_green} icon="🟢" accent="green" />
              <KpiCard label="Health Red" value={p!.health_red} icon="🔴"
                accent={p!.health_red > 0 ? 'red' : 'default'}
                sub={`${p!.health_yellow} yellow`} />
            </div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {statusData.length > 0 && (
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <h3 className="mb-3 text-sm font-semibold text-slate-700">Projects by Status</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={statusData} margin={{ top: 0, right: 8, left: -20, bottom: 40 }}>
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
                      <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
              {healthData.length > 0 && (
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <h3 className="mb-3 text-sm font-semibold text-slate-700">Project Health</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie data={healthData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70}>
                        {healthData.map(e => <Cell key={e.name} fill={e.color} />)}
                      </Pie>
                      <Legend />
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </section>

          {/* Labor + Safety + Service */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-slate-700">Labor, Safety &amp; Service</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <KpiCard label="Labor Hours MTD" value={l!.total_hours_mtd.toFixed(1)} icon="⏱️" accent="blue"
                sub={`${l!.overtime_hours_mtd.toFixed(1)} OT hrs (${l!.overtime_rate}%)`} />
              <KpiCard label="Safety Incidents" value={s!.total_incidents} icon="🚨"
                accent={s!.total_incidents > 0 ? 'red' : 'green'}
                sub={`${s!.recordable_incidents} recordable`} />
              <KpiCard label="Open Service Tickets" value={svc!.open_tickets} icon="🔧"
                accent={svc!.open_tickets > 0 ? 'amber' : 'default'} />
              <KpiCard label="Active Warranties" value={svc!.active_warranties} icon="🛡️" accent="indigo" />
            </div>
          </section>
        </>
      )}

      {/* Forecast */}
      {forecast && (
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-700">6-Month Forecast</h2>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Cash Flow Forecast</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={forecast.cash_flow} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
                  <Legend />
                  <Area type="monotone" dataKey="inflows" name="Inflows" stroke="#22c55e" fill="#dcfce7" strokeWidth={2} />
                  <Area type="monotone" dataKey="outflows" name="Outflows" stroke="#ef4444" fill="#fee2e2" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Pipeline Revenue Forecast</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={forecast.pipeline} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
                  <Bar dataKey="expected_revenue" name="Expected Revenue" fill="#7C3AED" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      )}

      {/* Saved Reports */}
      {reports && reports.results.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-700">Saved Reports</h2>
          <div className="rounded-xl border border-slate-200 bg-white divide-y divide-slate-50">
            {reports.results.map((report) => (
              <div key={report.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">{report.name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {REPORT_TYPE_LABELS[report.report_type] ?? report.report_type}
                    {report.description && ` · ${report.description}`}
                  </p>
                </div>
                <div className="text-right">
                  {report.last_run_at && (
                    <p className="text-xs text-slate-400">
                      Last run {new Date(report.last_run_at).toLocaleDateString()}
                    </p>
                  )}
                  <p className="text-xs text-slate-400">By {report.created_by_name ?? '—'}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
