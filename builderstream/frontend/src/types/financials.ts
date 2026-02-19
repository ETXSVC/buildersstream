export type InvoiceStatus = 'draft' | 'sent' | 'viewed' | 'partial' | 'paid' | 'overdue' | 'void';
export type ChangeOrderStatus = 'draft' | 'submitted' | 'approved' | 'rejected';
export type POStatus = 'draft' | 'sent' | 'partial' | 'received' | 'closed';
export type ExpenseStatus = 'pending' | 'approved' | 'rejected';

export interface Budget {
  id: string;
  project: string;
  project_name: string;
  cost_code: string | null;
  cost_code_display: string | null;
  description: string;
  budgeted_amount: string;
  committed_amount: string;
  actual_amount: string;
  variance: string;
  variance_percent: string;
}

export interface Invoice {
  id: string;
  project: string;
  project_name: string;
  invoice_number: string;
  status: InvoiceStatus;
  client: string | null;
  client_name: string | null;
  subtotal: string;
  tax_amount: string;
  retainage_amount: string;
  total: string;
  amount_paid: string;
  balance_due: string;
  issue_date: string;
  due_date: string | null;
  paid_date: string | null;
  sent_at: string | null;
}

export interface ChangeOrder {
  id: string;
  project: string;
  project_name: string;
  number: number;
  title: string;
  status: ChangeOrderStatus;
  amount: string;
  reason: string;
  submitted_at: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface PurchaseOrder {
  id: string;
  project: string;
  project_name: string;
  po_number: string;
  vendor_name: string;
  status: POStatus;
  subtotal: string;
  total: string;
  ordered_date: string | null;
  expected_delivery: string | null;
  created_at: string;
}

export interface Expense {
  id: string;
  project: string;
  project_name: string;
  description: string;
  amount: string;
  expense_date: string;
  category: string;
  status: ExpenseStatus;
  vendor: string | null;
}

export interface JobCostSummary {
  project_id: string;
  project_name: string;
  total_budget: number;
  total_committed: number;
  total_actual: number;
  total_variance: number;
  variance_percent: number;
  budget_by_cost_code: {
    cost_code: string;
    description: string;
    budgeted: number;
    actual: number;
    variance: number;
  }[];
}

export interface CashFlowMonth {
  month: string;
  invoiced: number;
  collected: number;
  expenses: number;
  net: number;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const INVOICE_STATUS_COLORS: Record<InvoiceStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  sent: 'bg-blue-100 text-blue-700',
  viewed: 'bg-purple-100 text-purple-700',
  partial: 'bg-amber-100 text-amber-700',
  paid: 'bg-green-100 text-green-700',
  overdue: 'bg-red-100 text-red-700',
  void: 'bg-slate-100 text-slate-400',
};

export const CO_STATUS_COLORS: Record<ChangeOrderStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  submitted: 'bg-blue-100 text-blue-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
};

export const PO_STATUS_COLORS: Record<POStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  sent: 'bg-blue-100 text-blue-700',
  partial: 'bg-amber-100 text-amber-700',
  received: 'bg-green-100 text-green-700',
  closed: 'bg-slate-100 text-slate-500',
};
