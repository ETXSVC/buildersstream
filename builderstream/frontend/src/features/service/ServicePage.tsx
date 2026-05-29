import { useState, useEffect, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useServiceRequests, useWarranties, useWarrantyClaims,
  useCreateServiceRequest, useUpdateServiceRequest, useDeleteServiceRequest,
  useCreateWarranty, useUpdateWarranty, useDeleteWarranty,
} from '@/hooks/useService';
import { useProjects } from '@/hooks/useProjects';
import {
  SERVICE_STATUS_COLORS,
  SERVICE_PRIORITY_COLORS,
  WARRANTY_STATUS_COLORS,
} from '@/types/service';
import type { ServiceRequest, Warranty } from '@/types/service';

type Tab = 'requests' | 'warranties' | 'claims';

function ServiceDashboard({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const { data: requestsData } = useServiceRequests({});
  const { data: warrantiesData } = useWarranties({});
  const { data: claimsData } = useWarrantyClaims({});

  const stats = useMemo(() => {
    const requests = requestsData?.results ?? [];
    const warranties = warrantiesData?.results ?? [];
    const claims = claimsData?.results ?? [];
    const openRequests = requests.filter(r => !['completed', 'closed', 'cancelled'].includes(r.status)).length;
    const highPriority = requests.filter(r => ['high', 'urgent'].includes(r.priority)).length;
    const activeWarranties = warranties.filter(w => w.status === 'active').length;
    const openClaims = claims.filter(c => !['resolved', 'closed'].includes(c.status)).length;
    const statusCounts = requests.reduce<Record<string, number>>((acc, r) => {
      acc[r.status] = (acc[r.status] ?? 0) + 1;
      return acc;
    }, {});
    const priorityCounts = requests.reduce<Record<string, number>>((acc, r) => {
      acc[r.priority] = (acc[r.priority] ?? 0) + 1;
      return acc;
    }, {});
    return { openRequests, highPriority, activeWarranties, openClaims, statusCounts, priorityCounts };
  }, [requestsData, warrantiesData, claimsData]);

  const PRIORITY_COLORS: Record<string, string> = {
    low: '#94a3b8', medium: '#60a5fa', high: '#f59e0b', urgent: '#ef4444',
  };

  const statusData = Object.entries(stats.statusCounts).map(([k, v]) => ({ name: k.replace('_', ' '), value: v }));
  const priorityData = Object.entries(stats.priorityCounts).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    color: PRIORITY_COLORS[k] ?? '#94a3b8',
  }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Open Requests" value={stats.openRequests} icon="🔧" accent={stats.openRequests > 0 ? 'amber' : 'default'} onClick={() => onNavigate('requests')} />
        <KpiCard label="High Priority" value={stats.highPriority} icon="🚨" accent={stats.highPriority > 0 ? 'red' : 'default'} onClick={() => onNavigate('requests')} />
        <KpiCard label="Active Warranties" value={stats.activeWarranties} icon="🛡️" accent="green" onClick={() => onNavigate('warranties')} />
        <KpiCard label="Open Claims" value={stats.openClaims} icon="📋" accent={stats.openClaims > 0 ? 'indigo' : 'default'} onClick={() => onNavigate('claims')} />
      </div>
      {(statusData.length > 0 || priorityData.length > 0) && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {statusData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Requests by Status</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={statusData} margin={{ top: 0, right: 8, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#60a5fa" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {priorityData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Requests by Priority</h3>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={priorityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65}>
                    {priorityData.map(e => <Cell key={e.name} fill={e.color} />)}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const ServicePage = () => {
  const [tab, setTab] = useState<Tab>('requests');
  const [editRequest, setEditRequest] = useState<ServiceRequest | null>(null);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [editWarranty, setEditWarranty] = useState<Warranty | null>(null);
  const [showWarrantyModal, setShowWarrantyModal] = useState(false);

  const openNewRequest = () => { setEditRequest(null); setShowRequestModal(true); };
  const openEditRequest = (r: ServiceRequest) => { setEditRequest(r); setShowRequestModal(true); };
  const openNewWarranty = () => { setEditWarranty(null); setShowWarrantyModal(true); };
  const openEditWarranty = (w: Warranty) => { setEditWarranty(w); setShowWarrantyModal(true); };

  const handleNavigate = (t: Tab) => {
    setTab(t);
    setTimeout(() => document.getElementById('service-list')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Service &amp; Warranty</h1>
        {tab === 'requests' && (
          <button type="button" onClick={openNewRequest}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 transition-colors">
            + New Request
          </button>
        )}
        {tab === 'warranties' && (
          <button type="button" onClick={openNewWarranty}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 transition-colors">
            + New Warranty
          </button>
        )}
      </div>
      <ServiceDashboard onNavigate={handleNavigate} />

      <div id="service-list" className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
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
              tab === key ? 'bg-blue-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'requests' && <ServiceRequestsTable onEdit={openEditRequest} />}
      {tab === 'warranties' && <WarrantiesTable onEdit={openEditWarranty} />}
      {tab === 'claims' && <WarrantyClaimsTable />}

      {showRequestModal && (
        <ServiceRequestModal
          record={editRequest}
          onClose={() => setShowRequestModal(false)}
        />
      )}
      {showWarrantyModal && (
        <WarrantyModal
          record={editWarranty}
          onClose={() => setShowWarrantyModal(false)}
        />
      )}
    </div>
  );
};

/* ── Service Requests Table ── */
function ServiceRequestsTable({ onEdit }: { onEdit: (r: ServiceRequest) => void }) {
  const { data, isLoading } = useServiceRequests({ page_size: '20' });
  const del = useDeleteServiceRequest();

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
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No service requests found.</td></tr>
          )}
          {data?.results.map((req) => (
            <tr key={req.id} className="group hover:bg-slate-50 transition-colors">
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
                {fmtDate(req.scheduled_date)}
              </td>
              <td className="px-4 py-3 text-center text-slate-600">
                {req.estimated_hours != null ? `${req.estimated_hours}h` : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SERVICE_STATUS_COLORS[req.status]}`}>
                  {req.status.replace('_', ' ')}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button type="button" onClick={() => onEdit(req)}
                    className="text-xs text-blue-600 hover:underline">Edit</button>
                  <button type="button" onClick={() => { if (confirm('Delete this service request?')) del.mutate(req.id); }}
                    className="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="service requests" />
    </div>
  );
}

/* ── Warranties Table ── */
function WarrantiesTable({ onEdit }: { onEdit: (w: Warranty) => void }) {
  const { data, isLoading } = useWarranties({ page_size: '20' });
  const del = useDeleteWarranty();

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
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No warranties found.</td></tr>
          )}
          {data?.results.map((w) => {
            const isExpiringSoon =
              w.status === 'active' &&
              new Date(w.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
            return (
              <tr key={w.id} className="group hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-slate-900 max-w-xs">
                  <p className="truncate">{w.item_description}</p>
                </td>
                <td className="px-4 py-3 text-slate-600 text-xs">{w.project_name ?? '—'}</td>
                <td className="px-4 py-3 text-slate-700 capitalize text-xs">{w.warranty_type.replace('_', ' ')}</td>
                <td className="px-4 py-3 text-slate-600 text-xs">{w.provider ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{fmtDate(w.start_date)}</td>
                <td className="px-4 py-3">
                  <span className={isExpiringSoon ? 'text-blue-600 font-medium' : 'text-slate-600'}>
                    {fmtDate(w.expiry_date)}
                    {isExpiringSoon && <span className="ml-1 text-xs">(soon)</span>}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  {w.claim_count > 0 ? (
                    <span className="text-blue-600 font-medium">{w.claim_count}</span>
                  ) : (
                    <span className="text-slate-300">0</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${WARRANTY_STATUS_COLORS[w.status]}`}>
                    {w.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button type="button" onClick={() => onEdit(w)}
                      className="text-xs text-blue-600 hover:underline">Edit</button>
                    <button type="button" onClick={() => { if (confirm('Delete this warranty?')) del.mutate(w.id); }}
                      className="text-xs text-red-500 hover:underline">Delete</button>
                  </div>
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

/* ── Warranty Claims Table (read-only) ── */
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
                {fmtDate(claim.claim_date)}
              </td>
              <td className="px-4 py-3 text-slate-700 max-w-xs">
                <p className="truncate text-xs">{claim.description}</p>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                  claim.status === 'resolved' ? 'bg-green-100 text-green-700' :
                  claim.status === 'denied' ? 'bg-red-100 text-red-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {claim.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 text-xs">
                {fmtDate(claim.resolved_date)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="claims" />
    </div>
  );
}

/* ── Service Request Modal ── */
function ServiceRequestModal({ record, onClose }: { record: ServiceRequest | null; onClose: () => void }) {
  const isEdit = !!record;
  const { data: projectsData } = useProjects();
  const create = useCreateServiceRequest();
  const update = useUpdateServiceRequest();

  const [form, setForm] = useState({
    title: '', description: '', priority: 'medium', status: 'new',
    project: '', scheduled_date: '', estimated_hours: '',
  });

  useEffect(() => {
    setForm({
      title: record?.title ?? '',
      description: record?.description ?? '',
      priority: record?.priority ?? 'medium',
      status: record?.status ?? 'new',
      project: record?.project ?? '',
      scheduled_date: record?.scheduled_date ?? '',
      estimated_hours: record?.estimated_hours != null ? String(record.estimated_hours) : '',
    });
  }, [record]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      title: form.title,
      description: form.description,
      priority: form.priority,
      status: form.status,
    };
    if (form.project) payload.project = form.project;
    if (form.scheduled_date) payload.scheduled_date = form.scheduled_date;
    if (form.estimated_hours) payload.estimated_hours = parseFloat(form.estimated_hours);

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Service Request' : 'New Service Request'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Title *">
          <input required title="Title" value={form.title} onChange={(e) => set('title', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <Field label="Description">
          <textarea title="Description" rows={3} value={form.description} onChange={(e) => set('description', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Priority">
            <select title="Priority" value={form.priority} onChange={(e) => set('priority', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </Field>
          <Field label="Status">
            <select title="Status" value={form.status} onChange={(e) => set('status', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="new">New</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="closed">Closed</option>
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
          <Field label="Est. Hours">
            <input title="Estimated hours" type="number" step="0.5" min="0" value={form.estimated_hours} onChange={(e) => set('estimated_hours', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </Field>
        </div>
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ── Warranty Modal ── */
function WarrantyModal({ record, onClose }: { record: Warranty | null; onClose: () => void }) {
  const isEdit = !!record;
  const { data: projectsData } = useProjects();
  const create = useCreateWarranty();
  const update = useUpdateWarranty();

  const [form, setForm] = useState({
    item_description: '', warranty_type: 'workmanship', status: 'active',
    project: '', start_date: '', expiry_date: '', provider: '',
  });

  useEffect(() => {
    setForm({
      item_description: record?.item_description ?? '',
      warranty_type: record?.warranty_type ?? 'workmanship',
      status: record?.status ?? 'active',
      project: record?.project ?? '',
      start_date: record?.start_date ?? '',
      expiry_date: record?.expiry_date ?? '',
      provider: record?.provider ?? '',
    });
  }, [record]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      item_description: form.item_description,
      warranty_type: form.warranty_type,
      status: form.status,
      start_date: form.start_date,
      expiry_date: form.expiry_date,
    };
    if (form.project) payload.project = form.project;
    if (form.provider) payload.provider = form.provider;

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Warranty' : 'New Warranty'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Item Description *">
          <input required title="Item description" value={form.item_description} onChange={(e) => set('item_description', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Warranty Type">
            <select title="Warranty type" value={form.warranty_type} onChange={(e) => set('warranty_type', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="workmanship">Workmanship</option>
              <option value="materials">Materials</option>
              <option value="manufacturer">Manufacturer</option>
              <option value="structural">Structural</option>
            </select>
          </Field>
          <Field label="Status">
            <select title="Status" value={form.status} onChange={(e) => set('status', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="claimed">Claimed</option>
              <option value="void">Void</option>
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
        <Field label="Provider">
          <input title="Provider" value={form.provider} onChange={(e) => set('provider', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Start Date *">
            <input title="Start date" required type="date" value={form.start_date} onChange={(e) => set('start_date', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </Field>
          <Field label="Expiry Date *">
            <input title="Expiry date" required type="date" value={form.expiry_date} onChange={(e) => set('expiry_date', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
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
