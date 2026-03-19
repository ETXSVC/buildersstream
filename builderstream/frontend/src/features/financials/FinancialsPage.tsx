import { useState, useEffect, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import { SubNav } from '@/components/SubNav';
const SUBNAV = [{ label: 'Financials', to: '/financials' }, { label: 'Payroll', to: '/payroll' }];
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useInvoices, useBudgets, useChangeOrders, usePurchaseOrders, useExpenses,
  useCreateExpense, useUpdateExpense, useDeleteExpense,
  useCreateChangeOrder, useUpdateChangeOrder, useDeleteChangeOrder,
  useCreatePurchaseOrder, useUpdatePurchaseOrder, useDeletePurchaseOrder,
  useCreateInvoice, useUpdateInvoice, useDeleteInvoice,
} from '@/hooks/useFinancials';
import { useProjects } from '@/hooks/useProjects';
import {
  INVOICE_STATUS_COLORS, CO_STATUS_COLORS, PO_STATUS_COLORS,
  type Invoice, type Expense, type ChangeOrder, type PurchaseOrder,
} from '@/types/financials';

type Tab = 'invoices' | 'expenses' | 'change-orders' | 'purchase-orders' | 'budgets';

function FinancialsDashboard({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const { data: invoicesData } = useInvoices({});
  const { data: expensesData } = useExpenses({});

  const stats = useMemo(() => {
    const invoices = invoicesData?.results ?? [];
    const expenses = expensesData?.results ?? [];
    const totalInvoiced = invoices.reduce((s, i) => s + parseFloat(i.total ?? '0'), 0);
    const outstanding = invoices.filter(i => ['sent', 'viewed', 'partial'].includes(i.status))
      .reduce((s, i) => s + parseFloat(i.balance_due ?? '0'), 0);
    const overdue = invoices.filter(i => i.status === 'overdue').length;
    const expenseTotal = expenses.reduce((s, e) => s + parseFloat(e.amount ?? '0'), 0);
    const statusCounts = invoices.reduce<Record<string, number>>((acc, i) => {
      acc[i.status] = (acc[i.status] ?? 0) + 1;
      return acc;
    }, {});
    return { totalInvoiced, outstanding, overdue, expenseTotal, statusCounts };
  }, [invoicesData, expensesData]);

  const statusColors: Record<string, string> = {
    draft: '#94a3b8', sent: '#60a5fa', viewed: '#818cf8',
    partial: '#f59e0b', paid: '#22c55e', overdue: '#ef4444', void: '#e2e8f0',
  };

  const invoiceStatusData = Object.entries(stats.statusCounts).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    color: statusColors[k] ?? '#94a3b8',
  }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Total Invoiced" value={`$${(stats.totalInvoiced / 1000).toFixed(1)}k`} icon="📄" accent="green" onClick={() => onNavigate('invoices')} />
        <KpiCard label="Outstanding" value={`$${(stats.outstanding / 1000).toFixed(1)}k`} icon="⏳" accent="amber" onClick={() => onNavigate('invoices')} />
        <KpiCard label="Overdue Invoices" value={stats.overdue} icon="⚠️" accent={stats.overdue > 0 ? 'red' : 'default'} onClick={() => onNavigate('invoices')} />
        <KpiCard label="Total Expenses" value={`$${(stats.expenseTotal / 1000).toFixed(1)}k`} icon="💳" onClick={() => onNavigate('expenses')} />
      </div>
      {invoiceStatusData.length > 0 && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Invoice Status</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={invoiceStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70}>
                  {invoiceStatusData.map(e => <Cell key={e.name} fill={e.color} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Invoice Count by Status</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={invoiceStatusData} margin={{ top: 0, right: 8, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {invoiceStatusData.map(e => <Cell key={e.name} fill={e.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export const FinancialsPage = () => {
  const [tab, setTab] = useState<Tab>('invoices');
  const [search, setSearch] = useState('');

  const tabs: { key: Tab; label: string }[] = [
    { key: 'invoices', label: 'Invoices' },
    { key: 'expenses', label: 'Expenses' },
    { key: 'change-orders', label: 'Change Orders' },
    { key: 'purchase-orders', label: 'Purchase Orders' },
    { key: 'budgets', label: 'Budgets' },
  ];

  const handleNavigate = (t: Tab) => {
    setTab(t);
    setTimeout(() => document.getElementById('financials-list')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="p-6">
      <SubNav items={SUBNAV} />
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Financials</h1>
        <div className="flex gap-2">
          {tab === 'expenses' && <NewExpenseButton search={search} />}
          {tab === 'change-orders' && <NewChangeOrderButton search={search} />}
          {tab === 'purchase-orders' && <NewPurchaseOrderButton search={search} />}
          {tab === 'invoices' && <NewInvoiceButton search={search} />}
        </div>
      </div>
      <FinancialsDashboard onNavigate={handleNavigate} />

      {/* Tabs */}
      <div id="financials-list" className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
              tab === t.key ? 'bg-blue-500 text-white' : 'text-slate-600 hover:text-slate-900',
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
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      {tab === 'invoices' && <InvoicesTable search={search} />}
      {tab === 'expenses' && <ExpensesTable search={search} />}
      {tab === 'change-orders' && <ChangeOrdersTable search={search} />}
      {tab === 'purchase-orders' && <PurchaseOrdersTable search={search} />}
      {tab === 'budgets' && <BudgetsTable search={search} />}
    </div>
  );
};

// ─── Helper buttons that own the modal state ─────────────────────────────────

function NewInvoiceButton({ search }: { search: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors"
      >
        <span className="text-lg leading-none">+</span> New Invoice
      </button>
      {open && <InvoiceModal onClose={() => setOpen(false)} />}
    </>
  );
}

function NewExpenseButton({ search: _ }: { search: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors"
      >
        <span className="text-lg leading-none">+</span> New Expense
      </button>
      {open && <ExpenseModal onClose={() => setOpen(false)} />}
    </>
  );
}

function NewChangeOrderButton({ search: _ }: { search: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors"
      >
        <span className="text-lg leading-none">+</span> New Change Order
      </button>
      {open && <ChangeOrderModal onClose={() => setOpen(false)} />}
    </>
  );
}

function NewPurchaseOrderButton({ search: _ }: { search: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors"
      >
        <span className="text-lg leading-none">+</span> New Purchase Order
      </button>
      {open && <PurchaseOrderModal onClose={() => setOpen(false)} />}
    </>
  );
}

// ─── Format helper ────────────────────────────────────────────────────────────

function fmt(val: string | number | null | undefined, decimals = 0) {
  if (val == null || val === '') return '—';
  const n = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(n)) return '—';
  return '$' + n.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

// ─── Tables ──────────────────────────────────────────────────────────────────

function InvoicesTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useInvoices(params);
  const deleteInvoice = useDeleteInvoice();
  const [editing, setEditing] = useState<Invoice | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No invoices found.</td></tr>
            )}
            {data?.results.map((inv) => (
              <tr key={inv.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">{inv.invoice_number}</td>
                <td className="px-4 py-3 text-slate-600">{inv.project_name}</td>
                <td className="px-4 py-3 text-slate-600">{inv.client_name ?? '—'}</td>
                <td className="px-4 py-3 text-slate-900 font-medium">{fmt(inv.total)}</td>
                <td className={`px-4 py-3 font-medium ${parseFloat(inv.balance_due) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {fmt(inv.balance_due)}
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {fmtDate(inv.due_date)}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${INVOICE_STATUS_COLORS[inv.status]}`}>
                    {inv.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(inv)}
                    onDelete={() => { if (confirm('Delete this invoice?')) deleteInvoice.mutate(inv.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="invoices" />
      </div>
      {editing && <InvoiceModal invoice={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

function ExpensesTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useExpenses(params);
  const deleteExpense = useDeleteExpense();
  const [editing, setEditing] = useState<Expense | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <Th>Project</Th>
              <Th>Description</Th>
              <Th>Category</Th>
              <Th>Vendor</Th>
              <Th>Amount</Th>
              <Th>Date</Th>
              <Th>Status</Th>
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No expenses found.</td></tr>
            )}
            {data?.results.map((exp) => (
              <tr key={exp.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-slate-600">{exp.project_name}</td>
                <td className="px-4 py-3 text-slate-900">{exp.description}</td>
                <td className="px-4 py-3 text-slate-600 capitalize">{exp.category.replace('_', ' ')}</td>
                <td className="px-4 py-3 text-slate-600">{exp.vendor ?? '—'}</td>
                <td className="px-4 py-3 font-medium text-slate-900">{fmt(exp.amount)}</td>
                <td className="px-4 py-3 text-slate-600">
                  {fmtDate(exp.expense_date)}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                    exp.status === 'approved' ? 'bg-green-100 text-green-700' :
                    exp.status === 'rejected' ? 'bg-red-100 text-red-600' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {exp.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(exp)}
                    onDelete={() => { if (confirm('Delete this expense?')) deleteExpense.mutate(exp.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="expenses" />
      </div>
      {editing && <ExpenseModal expense={editing} onClose={() => setEditing(null)} />}
    </>
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
  const deleteCO = useDeleteChangeOrder();
  const [editing, setEditing] = useState<ChangeOrder | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No change orders found.</td></tr>
            )}
            {data?.results.map((co) => (
              <tr key={co.id} className="group hover:bg-slate-50 transition-colors">
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
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(co)}
                    onDelete={() => { if (confirm('Delete this change order?')) deleteCO.mutate(co.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="change orders" />
      </div>
      {editing && <ChangeOrderModal changeOrder={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

function PurchaseOrdersTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = usePurchaseOrders(params);
  const deletePO = useDeletePurchaseOrder();
  const [editing, setEditing] = useState<PurchaseOrder | null>(null);

  if (isLoading) return <Spinner />;
  return (
    <>
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
              <Th><span className="sr-only">Actions</span></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No purchase orders found.</td></tr>
            )}
            {data?.results.map((po) => (
              <tr key={po.id} className="group hover:bg-slate-50 transition-colors">
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
                  {fmtDate(po.expected_delivery)}
                </td>
                <td className="px-4 py-3">
                  <RowActions
                    onEdit={() => setEditing(po)}
                    onDelete={() => { if (confirm('Delete this purchase order?')) deletePO.mutate(po.id); }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination count={data?.count} shown={data?.results.length} label="purchase orders" />
      </div>
      {editing && <PurchaseOrderModal purchaseOrder={editing} onClose={() => setEditing(null)} />}
    </>
  );
}

// ─── Modals ───────────────────────────────────────────────────────────────────

function InvoiceModal({ invoice, onClose }: { invoice?: Invoice; onClose: () => void }) {
  const { data: projectsData } = useProjects();
  const create = useCreateInvoice();
  const update = useUpdateInvoice();
  const isEdit = !!invoice;

  const [form, setForm] = useState({
    project: invoice?.project ?? '',
    title: '',
    due_date: invoice?.due_date ?? '',
    status: invoice?.status ?? 'draft',
  });

  useEffect(() => {
    setForm({
      project: invoice?.project ?? '',
      title: '',
      due_date: invoice?.due_date ?? '',
      status: invoice?.status ?? 'draft',
    });
  }, [invoice]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      status: form.status,
      due_date: form.due_date || null,
    };
    if (!isEdit) {
      if (!form.project) return;
      payload.project = form.project;
    }
    if (isEdit) {
      update.mutate({ id: invoice.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit Invoice' : 'New Invoice'} onClose={onClose}>
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
        <Field label="Status">
          <select
            title="Status"
            value={form.status}
            onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
            className={selectCls}
          >
            {['draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'void'].map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </Field>
        <Field label="Due Date">
          <input
            type="date"
            title="Due Date"
            value={form.due_date}
            onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

function ExpenseModal({ expense, onClose }: { expense?: Expense; onClose: () => void }) {
  const { data: projectsData } = useProjects();
  const create = useCreateExpense();
  const update = useUpdateExpense();
  const isEdit = !!expense;

  const [form, setForm] = useState({
    project: expense?.project ?? '',
    expense_type: expense?.category ?? 'materials',
    vendor_name: expense?.vendor ?? '',
    description: expense?.description ?? '',
    amount: expense?.amount ?? '',
    expense_date: expense?.expense_date ?? '',
  });

  useEffect(() => {
    setForm({
      project: expense?.project ?? '',
      expense_type: expense?.category ?? 'materials',
      vendor_name: expense?.vendor ?? '',
      description: expense?.description ?? '',
      amount: expense?.amount ?? '',
      expense_date: expense?.expense_date ?? '',
    });
  }, [expense]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      expense_type: form.expense_type,
      vendor_name: form.vendor_name,
      description: form.description,
      amount: form.amount || null,
      expense_date: form.expense_date || null,
    };
    if (!isEdit && form.project) payload.project = form.project;
    if (isEdit) {
      update.mutate({ id: expense.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  const expenseTypes = ['materials', 'labor', 'equipment', 'subcontractor', 'permits', 'insurance', 'overhead', 'other'];

  return (
    <Modal title={isEdit ? 'Edit Expense' : 'New Expense'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isEdit && (
          <Field label="Project">
            <select
              title="Project"
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
        <Field label="Category">
          <select
            title="Category"
            value={form.expense_type}
            onChange={(e) => setForm((f) => ({ ...f, expense_type: e.target.value }))}
            className={selectCls}
          >
            {expenseTypes.map((t) => (
              <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
            ))}
          </select>
        </Field>
        <Field label="Description *">
          <input
            type="text"
            title="Description"
            required
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            className={inputCls}
            placeholder="Brief description…"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Amount">
            <input
              type="number"
              title="Amount"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
          <Field label="Date">
            <input
              type="date"
              title="Expense Date"
              value={form.expense_date}
              onChange={(e) => setForm((f) => ({ ...f, expense_date: e.target.value }))}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Vendor">
          <input
            type="text"
            title="Vendor"
            value={form.vendor_name}
            onChange={(e) => setForm((f) => ({ ...f, vendor_name: e.target.value }))}
            className={inputCls}
            placeholder="Vendor name…"
          />
        </Field>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

function ChangeOrderModal({ changeOrder, onClose }: { changeOrder?: ChangeOrder; onClose: () => void }) {
  const { data: projectsData } = useProjects();
  const create = useCreateChangeOrder();
  const update = useUpdateChangeOrder();
  const isEdit = !!changeOrder;

  const [form, setForm] = useState({
    project: changeOrder?.project ?? '',
    title: changeOrder?.title ?? '',
    reason: changeOrder?.reason ?? '',
    amount: changeOrder?.amount ?? '',
    status: changeOrder?.status ?? 'draft',
  });

  useEffect(() => {
    setForm({
      project: changeOrder?.project ?? '',
      title: changeOrder?.title ?? '',
      reason: changeOrder?.reason ?? '',
      amount: changeOrder?.amount ?? '',
      status: changeOrder?.status ?? 'draft',
    });
  }, [changeOrder]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      title: form.title,
      reason: form.reason,
      amount: form.amount || '0',
      status: form.status,
    };
    if (!isEdit && form.project) payload.project = form.project;
    if (isEdit) {
      update.mutate({ id: changeOrder.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit Change Order' : 'New Change Order'} onClose={onClose}>
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
        <Field label="Title *">
          <input
            type="text"
            title="Title"
            required
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            className={inputCls}
            placeholder="Change order title…"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Amount ($)">
            <input
              type="number"
              title="Amount"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className={inputCls}
              placeholder="0.00"
            />
          </Field>
          <Field label="Status">
            <select
              title="Status"
              value={form.status}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className={selectCls}
            >
              {['draft', 'submitted', 'approved', 'rejected'].map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </Field>
        </div>
        <Field label="Reason">
          <textarea
            title="Reason"
            value={form.reason}
            onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
            rows={3}
            className={inputCls}
            placeholder="Reason for change order…"
          />
        </Field>
        <ModalActions onClose={onClose} isPending={create.isPending || update.isPending} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

function PurchaseOrderModal({ purchaseOrder, onClose }: { purchaseOrder?: PurchaseOrder; onClose: () => void }) {
  const { data: projectsData } = useProjects();
  const create = useCreatePurchaseOrder();
  const update = useUpdatePurchaseOrder();
  const isEdit = !!purchaseOrder;

  const [form, setForm] = useState({
    project: purchaseOrder?.project ?? '',
    vendor_name: purchaseOrder?.vendor_name ?? '',
    status: purchaseOrder?.status ?? 'draft',
    expected_delivery: purchaseOrder?.expected_delivery ?? '',
  });

  useEffect(() => {
    setForm({
      project: purchaseOrder?.project ?? '',
      vendor_name: purchaseOrder?.vendor_name ?? '',
      status: purchaseOrder?.status ?? 'draft',
      expected_delivery: purchaseOrder?.expected_delivery ?? '',
    });
  }, [purchaseOrder]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      vendor_name: form.vendor_name,
      status: form.status,
      expected_delivery: form.expected_delivery || null,
    };
    if (!isEdit && form.project) payload.project = form.project;
    if (isEdit) {
      update.mutate({ id: purchaseOrder.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit Purchase Order' : 'New Purchase Order'} onClose={onClose}>
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
        <Field label="Vendor Name *">
          <input
            type="text"
            title="Vendor Name"
            required
            value={form.vendor_name}
            onChange={(e) => setForm((f) => ({ ...f, vendor_name: e.target.value }))}
            className={inputCls}
            placeholder="Vendor name…"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Status">
            <select
              title="Status"
              value={form.status}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className={selectCls}
            >
              {['draft', 'sent', 'partial', 'received', 'closed'].map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </Field>
          <Field label="Expected Delivery">
            <input
              type="date"
              title="Expected Delivery"
              value={form.expected_delivery}
              onChange={(e) => setForm((f) => ({ ...f, expected_delivery: e.target.value }))}
              className={inputCls}
            />
          </Field>
        </div>
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

const inputCls = 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400';
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
      <div className="w-full max-w-md rounded-2xl bg-white shadow-xl">
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
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
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
