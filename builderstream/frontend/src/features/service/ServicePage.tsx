import { useState } from 'react';
import { useServiceRequests, useWarranties, useWarrantyClaims } from '@/hooks/useService';
import {
  SERVICE_STATUS_COLORS,
  SERVICE_PRIORITY_COLORS,
  WARRANTY_STATUS_COLORS,
} from '@/types/service';

type Tab = 'requests' | 'warranties' | 'claims';

export const ServicePage = () => {
  const [tab, setTab] = useState<Tab>('requests');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Service & Warranty</h1>
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {([
          { key: 'requests', label: 'Service Requests' },
          { key: 'warranties', label: 'Warranties' },
          { key: 'claims', label: 'Warranty Claims' },
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

      {tab === 'requests' && <ServiceRequestsTable />}
      {tab === 'warranties' && <WarrantiesTable />}
      {tab === 'claims' && <WarrantyClaimsTable />}
    </div>
  );
};

function ServiceRequestsTable() {
  const { data, isLoading } = useServiceRequests({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Request #</Th>
            <Th>Title</Th>
            <Th>Client</Th>
            <Th>Priority</Th>
            <Th>Assigned To</Th>
            <Th>Scheduled</Th>
            <Th>Est. Hours</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No service requests found.</td></tr>
          )}
          {data?.results.map((req) => (
            <tr key={req.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{req.request_number}</td>
              <td className="px-4 py-3 text-slate-900 max-w-xs">
                <p className="truncate">{req.title}</p>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{req.client_name ?? '—'}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${SERVICE_PRIORITY_COLORS[req.priority]}`}>
                  {req.priority}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{req.assigned_to_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {req.scheduled_date ? new Date(req.scheduled_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3 text-center text-slate-600">
                {req.estimated_hours != null ? `${req.estimated_hours}h` : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SERVICE_STATUS_COLORS[req.status]}`}>
                  {req.status.replace('_', ' ')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="service requests" />
    </div>
  );
}

function WarrantiesTable() {
  const { data, isLoading } = useWarranties({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Item</Th>
            <Th>Project</Th>
            <Th>Type</Th>
            <Th>Provider</Th>
            <Th>Start Date</Th>
            <Th>Expiry</Th>
            <Th>Claims</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No warranties found.</td></tr>
          )}
          {data?.results.map((w) => {
            const isExpiringSoon =
              w.status === 'active' &&
              new Date(w.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
            return (
              <tr key={w.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-slate-900 max-w-xs">
                  <p className="truncate">{w.item_description}</p>
                </td>
                <td className="px-4 py-3 text-slate-600 text-xs">{w.project_name ?? '—'}</td>
                <td className="px-4 py-3 text-slate-700 capitalize text-xs">{w.warranty_type.replace('_', ' ')}</td>
                <td className="px-4 py-3 text-slate-600 text-xs">{w.provider ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{new Date(w.start_date).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <span className={isExpiringSoon ? 'text-amber-600 font-medium' : 'text-slate-600'}>
                    {new Date(w.expiry_date).toLocaleDateString()}
                    {isExpiringSoon && <span className="ml-1 text-xs">(soon)</span>}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  {w.claim_count > 0 ? (
                    <span className="text-amber-600 font-medium">{w.claim_count}</span>
                  ) : (
                    <span className="text-slate-300">0</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${WARRANTY_STATUS_COLORS[w.status]}`}>
                    {w.status}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="warranties" />
    </div>
  );
}

function WarrantyClaimsTable() {
  const { data, isLoading } = useWarrantyClaims({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Warranty Item</Th>
            <Th>Project</Th>
            <Th>Claim Date</Th>
            <Th>Description</Th>
            <Th>Status</Th>
            <Th>Resolved</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No warranty claims found.</td></tr>
          )}
          {data?.results.map((claim) => (
            <tr key={claim.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 text-slate-900 text-xs max-w-xs">
                <p className="truncate">{claim.warranty_item}</p>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{claim.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {new Date(claim.claim_date).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 text-slate-700 max-w-xs">
                <p className="truncate text-xs">{claim.description}</p>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                  claim.status === 'resolved' ? 'bg-green-100 text-green-700' :
                  claim.status === 'denied' ? 'bg-red-100 text-red-700' :
                  'bg-amber-100 text-amber-700'
                }`}>
                  {claim.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">
                {claim.resolved_date ? new Date(claim.resolved_date).toLocaleDateString() : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="claims" />
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
