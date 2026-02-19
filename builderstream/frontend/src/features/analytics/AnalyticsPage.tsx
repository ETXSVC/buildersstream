import { useReportSummary, useReports } from '@/hooks/useAnalytics';
import { REPORT_TYPE_LABELS } from '@/types/analytics';

export const AnalyticsPage = () => {
  const { data: summary, isLoading } = useReportSummary();
  const { data: reports } = useReports({ page_size: '20' });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>

      {/* KPI Cards */}
      {isLoading ? (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      ) : summary?.kpis ? (
        <KPIGrid kpis={summary.kpis} generatedAt={summary.generated_at} />
      ) : null}

      {/* Reports List */}
      {reports && reports.results.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="text-sm font-semibold text-slate-700">Saved Reports</h2>
          </div>
          <div className="divide-y divide-slate-50">
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
        </div>
      )}
    </div>
  );
};

function KPIGrid({ kpis, generatedAt }: { kpis: NonNullable<ReturnType<typeof useReportSummary>['data']>['kpis']; generatedAt: string }) {
  const cards = [
    {
      label: 'Revenue MTD',
      value: fmtCurrency(kpis.revenue_mtd),
      sub: `YTD: ${fmtCurrency(kpis.revenue_ytd)}`,
      color: 'text-green-600',
    },
    {
      label: 'Active Projects',
      value: String(kpis.active_projects),
      sub: `${kpis.projects_on_schedule} on schedule`,
      color: 'text-slate-900',
    },
    {
      label: 'Projects Over Budget',
      value: String(kpis.projects_over_budget),
      sub: kpis.avg_project_margin != null ? `Avg margin ${kpis.avg_project_margin.toFixed(1)}%` : '',
      color: kpis.projects_over_budget > 0 ? 'text-red-600' : 'text-slate-900',
    },
    {
      label: 'Open Bids',
      value: String(kpis.open_bids),
      sub: kpis.win_rate != null ? `Win rate ${kpis.win_rate.toFixed(0)}%` : '',
      color: 'text-slate-900',
    },
    {
      label: 'Overdue Invoices',
      value: String(kpis.overdue_invoices_count),
      sub: fmtCurrency(kpis.overdue_invoices_amount),
      color: kpis.overdue_invoices_count > 0 ? 'text-red-600' : 'text-slate-900',
    },
    {
      label: 'Open RFIs',
      value: String(kpis.open_rfis),
      sub: `${kpis.pending_submittals} pending submittals`,
      color: kpis.open_rfis > 5 ? 'text-amber-600' : 'text-slate-900',
    },
    {
      label: 'Field Hours (wk)',
      value: kpis.field_hours_this_week.toLocaleString(),
      sub: 'current week',
      color: 'text-slate-900',
    },
    {
      label: 'Safety Incidents YTD',
      value: String(kpis.safety_incidents_ytd),
      sub: 'year to date',
      color: kpis.safety_incidents_ytd > 0 ? 'text-red-600' : 'text-green-600',
    },
  ];

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-700">Key Performance Indicators</h2>
        <span className="text-xs text-slate-400">
          Updated {new Date(generatedAt).toLocaleString()}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs text-slate-500 mb-1">{card.label}</p>
            <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
            {card.sub && <p className="text-xs text-slate-400 mt-1">{card.sub}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

function fmtCurrency(val: number | null | undefined) {
  if (val == null) return '—';
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toLocaleString()}`;
}
