import { useState } from 'react';
import { useInspections, useDeficiencies, useSafetyIncidents } from '@/hooks/useQualitySafety';
import {
  INSPECTION_STATUS_COLORS,
  DEFICIENCY_STATUS_COLORS,
  SEVERITY_COLORS,
  INCIDENT_SEVERITY_COLORS,
} from '@/types/quality-safety';

type Tab = 'inspections' | 'deficiencies' | 'incidents';

export const QualitySafetyPage = () => {
  const [tab, setTab] = useState<Tab>('inspections');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Quality & Safety</h1>
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['inspections', 'deficiencies', 'incidents'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              tab === t ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t === 'incidents' ? 'Safety Incidents' : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'inspections' && <InspectionsTable />}
      {tab === 'deficiencies' && <DeficienciesTable />}
      {tab === 'incidents' && <IncidentsTable />}
    </div>
  );
};

function InspectionsTable() {
  const { data, isLoading } = useInspections({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Inspection #</Th>
            <Th>Project</Th>
            <Th>Type</Th>
            <Th>Inspector</Th>
            <Th>Scheduled</Th>
            <Th>Score</Th>
            <Th>Pass / Fail</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No inspections found.</td></tr>
          )}
          {data?.results.map((ins) => (
            <tr key={ins.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{ins.inspection_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{ins.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700 capitalize">{ins.inspection_type.replace('_', ' ')}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{ins.inspector_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {ins.scheduled_date ? new Date(ins.scheduled_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3 text-center">
                {ins.score != null ? (
                  <span className={`font-semibold ${ins.score >= 80 ? 'text-green-600' : ins.score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>
                    {ins.score}
                  </span>
                ) : '—'}
              </td>
              <td className="px-4 py-3 text-center">
                {ins.passed != null ? (
                  <span className={`text-xs font-medium ${ins.passed ? 'text-green-600' : 'text-red-600'}`}>
                    {ins.passed ? '✓ Pass' : '✗ Fail'}
                  </span>
                ) : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${INSPECTION_STATUS_COLORS[ins.status]}`}>
                  {ins.status.replace('_', ' ')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="inspections" />
    </div>
  );
}

function DeficienciesTable() {
  const { data, isLoading } = useDeficiencies({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Description</Th>
            <Th>Project</Th>
            <Th>Inspection</Th>
            <Th>Severity</Th>
            <Th>Assigned To</Th>
            <Th>Due Date</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No deficiencies found.</td></tr>
          )}
          {data?.results.map((def) => (
            <tr key={def.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 text-slate-900 max-w-xs">
                <p className="truncate">{def.description}</p>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{def.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{def.inspection_number ?? '—'}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${SEVERITY_COLORS[def.severity]}`}>
                  {def.severity}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{def.assigned_to_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {def.due_date ? (
                  <span className={new Date(def.due_date) < new Date() && def.status !== 'resolved' ? 'text-red-600 font-medium' : ''}>
                    {new Date(def.due_date).toLocaleDateString()}
                  </span>
                ) : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${DEFICIENCY_STATUS_COLORS[def.status]}`}>
                  {def.status.replace('_', ' ')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="deficiencies" />
    </div>
  );
}

function IncidentsTable() {
  const { data, isLoading } = useSafetyIncidents({ page_size: '20' });
  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Incident #</Th>
            <Th>Project</Th>
            <Th>Type</Th>
            <Th>Severity</Th>
            <Th>Reported By</Th>
            <Th>Date</Th>
            <Th>Injuries</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No safety incidents found.</td></tr>
          )}
          {data?.results.map((inc) => (
            <tr key={inc.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{inc.incident_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{inc.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700 capitalize">{inc.incident_type.replace('_', ' ')}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${INCIDENT_SEVERITY_COLORS[inc.severity]}`}>
                  {inc.severity}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{inc.reported_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {new Date(inc.incident_date).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 text-center">
                {inc.injuries_count > 0 ? (
                  <span className="text-red-600 font-semibold">{inc.injuries_count}</span>
                ) : (
                  <span className="text-slate-300">0</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                  inc.is_resolved ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                }`}>
                  {inc.is_resolved ? 'Resolved' : 'Open'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="incidents" />
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
