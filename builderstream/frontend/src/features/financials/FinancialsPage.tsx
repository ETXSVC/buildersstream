import { useState } from 'react';
import { useInvoices, useBudgets, useChangeOrders, usePurchaseOrders } from '@/hooks/useFinancials';
import {
  INVOICE_STATUS_COLORS, CO_STATUS_COLORS, PO_STATUS_COLORS,
} from '@/types/financials';

type Tab = 'invoices' | 'budgets' | 'change-orders' | 'purchase-orders';

export const FinancialsPage = () => {
  const [tab, setTab] = useState<Tab>('invoices');
  const [search, setSearch] = useState('');

  const tabs: { key: Tab; label: string }[] = [
    { key: 'invoices', label: 'Invoices' },
    { key: 'budgets', label: 'Budgets' },
    { key: 'change-orders', label: 'Change Orders' },
    { key: 'purchase-orders', label: 'Purchase Orders' },
  ];

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Financials</h1>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
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

      {/* Search */}
      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${tab.replace('-', ' ')}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {tab === 'invoices' && <InvoicesTable search={search} />}
      {tab === 'budgets' && <BudgetsTable search={search} />}
      {tab === 'change-orders' && <ChangeOrdersTable search={search} />}
      {tab === 'purchase-orders' && <PurchaseOrdersTable search={search} />}
    </div>
  );
};

function fmt(val: string | number | null | undefined, decimals = 0) {
  if (val == null || val === '') return '—';
  const n = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(n)) return '—';
  return '$' + n.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function InvoicesTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useInvoices(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Invoice #</Th>
            <Th>Project</Th>
            <Th>Client</Th>
            <Th>Total</Th>
            <Th>Balance Due</Th>
            <Th>Due Date</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No invoices found.</td></tr>
          )}
          {data?.results.map((inv) => (
            <tr key={inv.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{inv.invoice_number}</td>
              <td className="px-4 py-3 text-slate-600">{inv.project_name}</td>
              <td className="px-4 py-3 text-slate-600">{inv.client_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-900 font-medium">{fmt(inv.total)}</td>
              <td className={`px-4 py-3 font-medium ${parseFloat(inv.balance_due) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {fmt(inv.balance_due)}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${INVOICE_STATUS_COLORS[inv.status]}`}>
                  {inv.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="invoices" />
    </div>
  );
}

function BudgetsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useBudgets(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Project</Th>
            <Th>Cost Code</Th>
            <Th>Description</Th>
            <Th>Budgeted</Th>
            <Th>Actual</Th>
            <Th>Variance</Th>
            <Th>Var %</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No budgets found.</td></tr>
          )}
          {data?.results.map((b) => {
            const variance = parseFloat(b.variance);
            return (
              <tr key={b.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-slate-600">{b.project_name}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-500">{b.cost_code_display ?? '—'}</td>
                <td className="px-4 py-3 text-slate-900">{b.description}</td>
                <td className="px-4 py-3 text-slate-900">{fmt(b.budgeted_amount)}</td>
                <td className="px-4 py-3 text-slate-900">{fmt(b.actual_amount)}</td>
                <td className={`px-4 py-3 font-medium ${variance < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {fmt(b.variance)}
                </td>
                <td className={`px-4 py-3 text-sm ${parseFloat(b.variance_percent) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {parseFloat(b.variance_percent).toFixed(1)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="budgets" />
    </div>
  );
}

function ChangeOrdersTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useChangeOrders(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>CO #</Th>
            <Th>Project</Th>
            <Th>Title</Th>
            <Th>Amount</Th>
            <Th>Status</Th>
            <Th>Submitted</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No change orders found.</td></tr>
          )}
          {data?.results.map((co) => (
            <tr key={co.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">CO-{String(co.number).padStart(3, '0')}</td>
              <td className="px-4 py-3 text-slate-600">{co.project_name}</td>
              <td className="px-4 py-3 text-slate-900">{co.title}</td>
              <td className={`px-4 py-3 font-medium ${parseFloat(co.amount) >= 0 ? 'text-green-700' : 'text-red-600'}`}>
                {fmt(co.amount)}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${CO_STATUS_COLORS[co.status]}`}>
                  {co.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-500">
                {co.submitted_at ? new Date(co.submitted_at).toLocaleDateString() : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="change orders" />
    </div>
  );
}

function PurchaseOrdersTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = usePurchaseOrders(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>PO #</Th>
            <Th>Project</Th>
            <Th>Vendor</Th>
            <Th>Total</Th>
            <Th>Status</Th>
            <Th>Expected Delivery</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No purchase orders found.</td></tr>
          )}
          {data?.results.map((po) => (
            <tr key={po.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{po.po_number}</td>
              <td className="px-4 py-3 text-slate-600">{po.project_name}</td>
              <td className="px-4 py-3 text-slate-900">{po.vendor_name}</td>
              <td className="px-4 py-3 font-medium text-slate-900">{fmt(po.total)}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PO_STATUS_COLORS[po.status]}`}>
                  {po.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-500">
                {po.expected_delivery ? new Date(po.expected_delivery).toLocaleDateString() : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="purchase orders" />
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
