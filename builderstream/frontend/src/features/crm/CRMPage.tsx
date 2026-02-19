import { useState } from 'react';
import { useContacts, useLeads, usePipelineStages } from '@/hooks/useCRM';
import { LEAD_STATUS_COLORS, PRIORITY_COLORS, SOURCE_LABELS } from '@/types/crm';

type View = 'leads' | 'contacts';

export const CRMPage = () => {
  const [view, setView] = useState<View>('leads');
  const [search, setSearch] = useState('');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">CRM</h1>
      </div>

      {/* View toggle */}
      <div className="mb-6 flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['leads', 'contacts'] as View[]).map((v) => (
          <button
            key={v}
            type="button"
            onClick={() => setView(v)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              view === v ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {v}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${view}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm w-full max-w-xs text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {view === 'leads' ? (
        <LeadsTable search={search} />
      ) : (
        <ContactsTable search={search} />
      )}
    </div>
  );
};

function LeadsTable({ search }: { search: string }) {
  const params: Record<string, string> = {};
  if (search) params.search = search;
  const { data, isLoading } = useLeads(params);
  const { data: stages } = usePipelineStages();

  const stageMap = Object.fromEntries((stages ?? []).map((s) => [s.id, s.name]));

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Lead</Th>
            <Th>Contact</Th>
            <Th>Stage</Th>
            <Th>Value</Th>
            <Th>Priority</Th>
            <Th>Source</Th>
            <Th>Score</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr>
              <td colSpan={8} className="px-4 py-8 text-center text-slate-400">No leads found.</td>
            </tr>
          )}
          {data?.results.map((lead) => (
            <tr key={lead.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3">
                <p className="font-medium text-slate-900">{lead.title}</p>
                {lead.company_name && <p className="text-xs text-slate-500">{lead.company_name}</p>}
              </td>
              <td className="px-4 py-3 text-slate-600">{lead.contact_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{lead.stage ? (stageMap[lead.stage] ?? lead.stage_name) : '—'}</td>
              <td className="px-4 py-3 text-slate-900">
                {lead.estimated_value ? `$${Number(lead.estimated_value).toLocaleString()}` : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_COLORS[lead.priority]}`}>
                  {lead.priority}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">{SOURCE_LABELS[lead.source] ?? lead.source}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full ${lead.lead_score >= 70 ? 'bg-green-500' : lead.lead_score >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                      style={{ width: `${lead.lead_score}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500">{lead.lead_score}</span>
                </div>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LEAD_STATUS_COLORS[lead.status]}`}>
                  {lead.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data && data.count > data.results.length && (
        <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
          Showing {data.results.length} of {data.count} leads
        </div>
      )}
    </div>
  );
}

function ContactsTable({ search }: { search: string }) {
  const { data, isLoading } = useContacts(search || undefined);

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Name</Th>
            <Th>Email</Th>
            <Th>Phone</Th>
            <Th>Company</Th>
            <Th>Title</Th>
            <Th>Score</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-slate-400">No contacts found.</td>
            </tr>
          )}
          {data?.results.map((contact) => (
            <tr key={contact.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-semibold text-amber-700">
                    {contact.first_name[0]}{contact.last_name[0]}
                  </div>
                  <span className="font-medium text-slate-900">{contact.full_name}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-600">{contact.email ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{contact.phone ?? contact.mobile_phone ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{contact.company_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{contact.job_title ?? '—'}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full ${contact.lead_score >= 70 ? 'bg-green-500' : contact.lead_score >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                      style={{ width: `${contact.lead_score}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500">{contact.lead_score}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data && data.count > data.results.length && (
        <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
          Showing {data.results.length} of {data.count} contacts
        </div>
      )}
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

function LoadingSpinner() {
  return (
    <div className="flex h-40 items-center justify-center">
      <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
    </div>
  );
}
