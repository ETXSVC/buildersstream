import { useState, useEffect, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useInspections, useDeficiencies, useSafetyIncidents,
  useCreateInspection, useUpdateInspection, useDeleteInspection,
  useCreateSafetyIncident, useUpdateSafetyIncident, useDeleteSafetyIncident,
} from '@/hooks/useQualitySafety';
import { useProjects } from '@/hooks/useProjects';
import {
  INSPECTION_STATUS_COLORS,
  DEFICIENCY_STATUS_COLORS,
  SEVERITY_COLORS,
  INCIDENT_SEVERITY_COLORS,
} from '@/types/quality-safety';
import type { Inspection, SafetyIncident } from '@/types/quality-safety';

type Tab = 'inspections' | 'deficiencies' | 'incidents';

function QualitySafetyDashboard({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const { data: inspData } = useInspections({});
  const { data: defData } = useDeficiencies({});
  const { data: incData } = useSafetyIncidents({});

  const stats = useMemo(() => {
    const inspections = inspData?.results ?? [];
    const deficiencies = defData?.results ?? [];
    const incidents = incData?.results ?? [];
    const total = inspections.length;
    const passed = inspections.filter(i => i.passed === true).length;
    const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
    const openDefs = deficiencies.filter(d => !['resolved', 'closed'].includes(d.status)).length;
    const critical = incidents.filter(i => ['recordable', 'lost_time'].includes(i.severity)).length;
    const resultCounts = inspections.reduce<Record<string, number>>((acc, i) => {
      const k = i.passed === true ? 'pass' : i.passed === false ? 'fail' : 'pending';
      acc[k] = (acc[k] ?? 0) + 1;
      return acc;
    }, {});
    const sevCounts = incidents.reduce<Record<string, number>>((acc, i) => {
      acc[i.severity] = (acc[i.severity] ?? 0) + 1;
      return acc;
    }, {});
    return { total, passRate, openDefs, incidentCount: incidents.length, critical, resultCounts, sevCounts };
  }, [inspData, defData, incData]);

  const resultData = Object.entries(stats.resultCounts).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    color: k === 'pass' ? '#22c55e' : k === 'fail' ? '#ef4444' : '#94a3b8',
  }));

  const sevData = Object.entries(stats.sevCounts).map(([k, v]) => ({
    name: k.replace('_', ' '),
    value: v,
  }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Inspections" value={stats.total} icon="🔍" onClick={() => onNavigate('inspections')} />
        <KpiCard label="Pass Rate" value={`${stats.passRate}%`} icon="✅" accent={stats.passRate >= 80 ? 'green' : stats.passRate >= 60 ? 'amber' : 'red'} onClick={() => onNavigate('inspections')} />
        <KpiCard label="Open Deficiencies" value={stats.openDefs} icon="⚠️" accent={stats.openDefs > 0 ? 'amber' : 'default'} onClick={() => onNavigate('deficiencies')} />
        <KpiCard label="Safety Incidents" value={stats.incidentCount} icon="🚨" accent={stats.critical > 0 ? 'red' : 'default'} sub={stats.critical > 0 ? `${stats.critical} recordable` : 'No recordable'} onClick={() => onNavigate('incidents')} />
      </div>
      {(resultData.length > 0 || sevData.length > 0) && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {resultData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Inspection Results</h3>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={resultData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65}>
                    {resultData.map(e => <Cell key={e.name} fill={e.color} />)}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          {sevData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Incidents by Severity</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={sevData} margin={{ top: 0, right: 8, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#f97316" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const QualitySafetyPage = () => {
  const [tab, setTab] = useState<Tab>('inspections');
  const [editInspection, setEditInspection] = useState<Inspection | null>(null);
  const [showInspectionModal, setShowInspectionModal] = useState(false);
  const [editIncident, setEditIncident] = useState<SafetyIncident | null>(null);
  const [showIncidentModal, setShowIncidentModal] = useState(false);

  const openNewInspection = () => { setEditInspection(null); setShowInspectionModal(true); };
  const openEditInspection = (i: Inspection) => { setEditInspection(i); setShowInspectionModal(true); };
  const openNewIncident = () => { setEditIncident(null); setShowIncidentModal(true); };
  const openEditIncident = (i: SafetyIncident) => { setEditIncident(i); setShowIncidentModal(true); };

  const handleNavigate = (t: Tab) => {
    setTab(t);
    setTimeout(() => document.getElementById('qs-list')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Quality &amp; Safety</h1>
        {tab === 'inspections' && (
          <button type="button" onClick={openNewInspection}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 transition-colors">
            + New Inspection
          </button>
        )}
        {tab === 'incidents' && (
          <button type="button" onClick={openNewIncident}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 transition-colors">
            + New Incident
          </button>
        )}
      </div>
      <QualitySafetyDashboard onNavigate={handleNavigate} />

      <div id="qs-list" className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['inspections', 'deficiencies', 'incidents'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              tab === t ? 'bg-blue-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t === 'incidents' ? 'Safety Incidents' : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'inspections' && <InspectionsTable onEdit={openEditInspection} />}
      {tab === 'deficiencies' && <DeficienciesTable />}
      {tab === 'incidents' && <IncidentsTable onEdit={openEditIncident} />}

      {showInspectionModal && (
        <InspectionModal
          record={editInspection}
          onClose={() => setShowInspectionModal(false)}
        />
      )}
      {showIncidentModal && (
        <SafetyIncidentModal
          record={editIncident}
          onClose={() => setShowIncidentModal(false)}
        />
      )}
    </div>
  );
};

/* ── Inspections Table ── */
function InspectionsTable({ onEdit }: { onEdit: (i: Inspection) => void }) {
  const { data, isLoading } = useInspections({ page_size: '20' });
  const del = useDeleteInspection();

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
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No inspections found.</td></tr>
          )}
          {data?.results.map((ins) => (
            <tr key={ins.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{ins.inspection_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{ins.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700 capitalize">{ins.inspection_type.replace('_', ' ')}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{ins.inspector_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {fmtDate(ins.scheduled_date)}
              </td>
              <td className="px-4 py-3 text-center">
                {ins.score != null ? (
                  <span className={`font-semibold ${ins.score >= 80 ? 'text-green-600' : ins.score >= 60 ? 'text-blue-600' : 'text-red-600'}`}>
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
              <td className="px-4 py-3">
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button type="button" onClick={() => onEdit(ins)}
                    className="text-xs text-blue-600 hover:underline">Edit</button>
                  <button type="button" onClick={() => { if (confirm('Delete this inspection?')) del.mutate(ins.id); }}
                    className="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="inspections" />
    </div>
  );
}

/* ── Deficiencies Table (read-only) ── */
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
                  <span className={new Date(def.due_date + 'T00:00:00') < new Date() && def.status !== 'resolved' ? 'text-red-600 font-medium' : ''}>
                    {fmtDate(def.due_date)}
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

/* ── Safety Incidents Table ── */
function IncidentsTable({ onEdit }: { onEdit: (i: SafetyIncident) => void }) {
  const { data, isLoading } = useSafetyIncidents({ page_size: '20' });
  const del = useDeleteSafetyIncident();

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
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No safety incidents found.</td></tr>
          )}
          {data?.results.map((inc) => (
            <tr key={inc.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{inc.incident_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{inc.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700 capitalize">{inc.incident_type.replace('_', ' ')}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${INCIDENT_SEVERITY_COLORS[inc.severity]}`}>
                  {inc.severity.replace('_', ' ')}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">{inc.reported_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {fmtDate(inc.incident_date)}
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
                  inc.is_resolved ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  {inc.is_resolved ? 'Resolved' : 'Open'}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button type="button" onClick={() => onEdit(inc)}
                    className="text-xs text-blue-600 hover:underline">Edit</button>
                  <button type="button" onClick={() => { if (confirm('Delete this incident?')) del.mutate(inc.id); }}
                    className="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="incidents" />
    </div>
  );
}

/* ── Inspection Modal ── */
function InspectionModal({ record, onClose }: { record: Inspection | null; onClose: () => void }) {
  const isEdit = !!record;
  const { data: projectsData } = useProjects();
  const create = useCreateInspection();
  const update = useUpdateInspection();

  const [form, setForm] = useState({
    inspection_type: 'quality', status: 'scheduled',
    project: '', scheduled_date: '', notes: '', score: '',
  });

  useEffect(() => {
    setForm({
      inspection_type: record?.inspection_type ?? 'quality',
      status: record?.status ?? 'scheduled',
      project: record?.project ?? '',
      scheduled_date: record?.scheduled_date ?? '',
      notes: record?.notes ?? '',
      score: record?.score != null ? String(record.score) : '',
    });
  }, [record]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      inspection_type: form.inspection_type,
      status: form.status,
    };
    if (form.project) payload.project = form.project;
    if (form.scheduled_date) payload.scheduled_date = form.scheduled_date;
    if (form.notes) payload.notes = form.notes;
    if (form.score) payload.score = parseInt(form.score, 10);

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Inspection' : 'New Inspection'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Field label="Type">
            <select title="Inspection type" value={form.inspection_type} onChange={(e) => set('inspection_type', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="quality">Quality</option>
              <option value="safety">Safety</option>
              <option value="framing">Framing</option>
              <option value="electrical">Electrical</option>
              <option value="plumbing">Plumbing</option>
              <option value="final">Final</option>
              <option value="other">Other</option>
            </select>
          </Field>
          <Field label="Status">
            <select title="Inspection status" value={form.status} onChange={(e) => set('status', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
              <option value="requires_action">Requires Action</option>
            </select>
          </Field>
        </div>
        <Field label="Project">
          <select title="Project" value={form.project} onChange={(e) => set('project', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">— No project —</option>
            {projectsData?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Scheduled Date">
            <input title="Scheduled date" type="date" value={form.scheduled_date} onChange={(e) => set('scheduled_date', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </Field>
          <Field label="Score (0–100)">
            <input title="Score" type="number" min="0" max="100" value={form.score} onChange={(e) => set('score', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea title="Notes" rows={3} value={form.notes} onChange={(e) => set('notes', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ── Safety Incident Modal ── */
function SafetyIncidentModal({ record, onClose }: { record: SafetyIncident | null; onClose: () => void }) {
  const isEdit = !!record;
  const { data: projectsData } = useProjects();
  const create = useCreateSafetyIncident();
  const update = useUpdateSafetyIncident();

  const [form, setForm] = useState({
    incident_type: 'near_miss', severity: 'near_miss',
    project: '', incident_date: '', description: '',
    injuries_count: '0', osha_recordable: 'false',
  });

  useEffect(() => {
    setForm({
      incident_type: record?.incident_type ?? 'near_miss',
      severity: record?.severity ?? 'near_miss',
      project: record?.project ?? '',
      incident_date: record?.incident_date ?? '',
      description: record?.description ?? '',
      injuries_count: record?.injuries_count != null ? String(record.injuries_count) : '0',
      osha_recordable: record?.osha_recordable ? 'true' : 'false',
    });
  }, [record]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      incident_type: form.incident_type,
      severity: form.severity,
      incident_date: form.incident_date,
      description: form.description,
      injuries_count: parseInt(form.injuries_count, 10) || 0,
      osha_recordable: form.osha_recordable === 'true',
    };
    if (form.project) payload.project = form.project;

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Safety Incident' : 'New Safety Incident'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Field label="Incident Type">
            <select title="Incident type" value={form.incident_type} onChange={(e) => set('incident_type', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="near_miss">Near Miss</option>
              <option value="injury">Injury</option>
              <option value="property_damage">Property Damage</option>
              <option value="fire">Fire</option>
              <option value="environmental">Environmental</option>
              <option value="other">Other</option>
            </select>
          </Field>
          <Field label="Severity">
            <select title="Severity" value={form.severity} onChange={(e) => set('severity', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="near_miss">Near Miss</option>
              <option value="first_aid">First Aid</option>
              <option value="recordable">Recordable</option>
              <option value="lost_time">Lost Time</option>
              <option value="fatality">Fatality</option>
            </select>
          </Field>
        </div>
        <Field label="Project">
          <select title="Project" value={form.project} onChange={(e) => set('project', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">— No project —</option>
            {projectsData?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Incident Date *">
          <input title="Incident date" required type="date" value={form.incident_date} onChange={(e) => set('incident_date', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <Field label="Description *">
          <textarea title="Description" required rows={3} value={form.description} onChange={(e) => set('description', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Injuries Count">
            <input title="Injuries count" type="number" min="0" value={form.injuries_count} onChange={(e) => set('injuries_count', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </Field>
          <Field label="OSHA Recordable">
            <select title="OSHA recordable" value={form.osha_recordable} onChange={(e) => set('osha_recordable', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="false">No</option>
              <option value="true">Yes</option>
            </select>
          </Field>
        </div>
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ── Shared UI ── */
function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
        </div>
        <div className="px-6 py-5 max-h-[75vh] overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      {children}
    </div>
  );
}

function ModalActions({ onClose, busy, isEdit }: { onClose: () => void; busy: boolean; isEdit: boolean }) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onClose}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
        Cancel
      </button>
      <button type="submit" disabled={busy}
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-60">
        {busy ? 'Saving…' : isEdit ? 'Save Changes' : 'Create'}
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
