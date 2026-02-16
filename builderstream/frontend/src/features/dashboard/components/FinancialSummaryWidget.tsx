import { WidgetCard } from './WidgetCard';
import type { FinancialSummary } from '@/types/dashboard';

interface FinancialSummaryWidgetProps {
  financial: FinancialSummary;
}

export const FinancialSummaryWidget = ({
  financial,
}: FinancialSummaryWidgetProps) => {
  const formatCurrency = (value: string) => {
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  const utilizationPct = parseFloat(financial.budget_utilization_pct);
  const utilizationColor =
    utilizationPct > 90
      ? 'text-red-600'
      : utilizationPct > 75
        ? 'text-yellow-600'
        : 'text-green-600';

  return (
    <WidgetCard
      title="Financial Summary"
      icon={
        <svg
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      }
    >
      {/* Revenue vs Costs */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-slate-600">Monthly Revenue</div>
          <div className="mt-1 text-2xl font-bold text-green-600">
            {formatCurrency(financial.monthly_revenue)}
          </div>
        </div>
        <div>
          <div className="text-sm text-slate-600">Monthly Costs</div>
          <div className="mt-1 text-2xl font-bold text-slate-900">
            {formatCurrency(financial.monthly_costs)}
          </div>
        </div>
      </div>

      {/* Budget Utilization */}
      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-medium text-slate-700">
            Budget Utilization
          </span>
          <span className={`text-sm font-bold ${utilizationColor}`}>
            {financial.budget_utilization_pct}%
          </span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className={`h-full transition-all ${
              utilizationPct > 90
                ? 'bg-red-500'
                : utilizationPct > 75
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(utilizationPct, 100)}%` }}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs text-slate-600">
          <span>Utilized: {formatCurrency(financial.budget_utilized)}</span>
          <span>Total: {formatCurrency(financial.total_budget)}</span>
        </div>
      </div>

      {/* Upcoming Invoices */}
      <div className="mt-6 rounded-lg bg-blue-50 p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-blue-900">
              Upcoming Invoices
            </div>
            <div className="mt-1 text-xs text-blue-700">
              {financial.upcoming_invoices_count} invoice
              {financial.upcoming_invoices_count !== 1 ? 's' : ''} due soon
            </div>
          </div>
          <div className="text-right">
            <div className="text-xl font-bold text-blue-900">
              {formatCurrency(financial.upcoming_invoices_total)}
            </div>
          </div>
        </div>
      </div>
    </WidgetCard>
  );
};
