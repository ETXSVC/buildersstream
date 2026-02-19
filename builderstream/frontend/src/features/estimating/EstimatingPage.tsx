import { useState } from 'react';
import { useEstimates, useProposals } from '@/hooks/useEstimating';
import { ESTIMATE_STATUS_COLORS, ESTIMATE_STATUS_LABELS, PROPOSAL_STATUS_COLORS } from '@/types/estimating';

type Tab = 'estimates' | 'proposals';

export const EstimatingPage = () => {
  const [tab, setTab] = useState<Tab>('estimates');
  const [search, setSearch] = useState('');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Estimating</h1>
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['estimates', 'proposals'] as Tab[]).map((t) => (
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

      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${tab}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {tab === 'estimates' && <EstimatesTable search={search} />}
      {tab === 'proposals' && <ProposalsTable search={search} />}
    </div>
  );
};

function EstimatesTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useEstimates(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Estimate #</Th>
            <Th>Name</Th>
            <Th>Project / Lead</Th>
            <Th>Sections</Th>
            <Th>Subtotal</Th>
            <Th>Total</Th>
            <Th>Valid Until</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No estimates found.</td></tr>
          )}
          {data?.results.map((est) => (
            <tr key={est.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{est.estimate_number}</td>
              <td className="px-4 py-3 text-slate-900">{est.name}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">
                {est.project_name ?? est.lead_title ?? '—'}
              </td>
              <td className="px-4 py-3 text-center text-slate-600">{est.section_count}</td>
              <td className="px-4 py-3 text-slate-900">${parseFloat(est.subtotal).toLocaleString()}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">${parseFloat(est.total).toLocaleString()}</td>
              <td className="px-4 py-3 text-slate-600">
                {est.valid_until ? new Date(est.valid_until).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ESTIMATE_STATUS_COLORS[est.status]}`}>
                  {ESTIMATE_STATUS_LABELS[est.status]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="estimates" />
    </div>
  );
}

function ProposalsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useProposals(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Proposal #</Th>
            <Th>Estimate</Th>
            <Th>Client</Th>
            <Th>Total</Th>
            <Th>Sent To</Th>
            <Th>Views</Th>
            <Th>Signed</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No proposals found.</td></tr>
          )}
          {data?.results.map((prop) => (
            <tr key={prop.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{prop.proposal_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{prop.estimate_number}</td>
              <td className="px-4 py-3 text-slate-900">{prop.client_name}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">${parseFloat(prop.total).toLocaleString()}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{prop.sent_to_email ?? '—'}</td>
              <td className="px-4 py-3 text-center">
                {prop.view_count > 0 ? (
                  <span className="inline-flex items-center gap-1 text-purple-600 text-xs font-medium">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {prop.view_count}
                  </span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-center">
                {prop.is_signed ? (
                  <span className="text-green-600 text-xs font-medium">
                    ✓ {prop.signed_by_name ?? 'Signed'}
                  </span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PROPOSAL_STATUS_COLORS[prop.status]}`}>
                  {prop.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="proposals" />
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
