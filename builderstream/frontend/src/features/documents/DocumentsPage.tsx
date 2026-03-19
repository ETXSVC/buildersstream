import { useState, useEffect, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useDocuments, useRFIs, useSubmittals, usePhotos,
  useCreateRFI, useUpdateRFI, useDeleteRFI,
  useCreateSubmittal, useUpdateSubmittal, useDeleteSubmittal,
} from '@/hooks/useDocuments';
import { useProjects } from '@/hooks/useProjects';
import { RFI_STATUS_COLORS, SUBMITTAL_STATUS_COLORS } from '@/types/documents';
import type { RFI, Submittal, RFIStatus, SubmittalStatus } from '@/types/documents';

type Tab = 'documents' | 'rfis' | 'submittals' | 'photos';

function DocumentsDashboard({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const { data: docsData } = useDocuments({});
  const { data: rfisData } = useRFIs({});
  const { data: submittalsData } = useSubmittals({});
  const { data: photosData } = usePhotos({});

  const stats = useMemo(() => {
    const rfis = rfisData?.results ?? [];
    const submittals = submittalsData?.results ?? [];
    const openRFIs = rfis.filter(r => !['closed', 'void'].includes(r.status)).length;
    const pendingSubmittals = submittals.filter(s => ['pending', 'submitted'].includes(s.status)).length;
    const rfiStatusCounts = rfis.reduce<Record<string, number>>((acc, r) => {
      acc[r.status] = (acc[r.status] ?? 0) + 1;
      return acc;
    }, {});
    const submStatusCounts = submittals.reduce<Record<string, number>>((acc, s) => {
      acc[s.status] = (acc[s.status] ?? 0) + 1;
      return acc;
    }, {});
    return {
      docs: docsData?.count ?? 0,
      openRFIs,
      pendingSubmittals,
      photos: photosData?.count ?? 0,
      rfiStatusCounts,
      submStatusCounts,
    };
  }, [docsData, rfisData, submittalsData, photosData]);

  const rfiData = Object.entries(stats.rfiStatusCounts).map(([k, v]) => ({ name: k, value: v }));
  const submData = Object.entries(stats.submStatusCounts).map(([k, v]) => ({ name: k, value: v }));

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Documents" value={stats.docs} icon="📁" onClick={() => onNavigate('documents')} />
        <KpiCard label="Open RFIs" value={stats.openRFIs} icon="❓" accent={stats.openRFIs > 0 ? 'amber' : 'default'} onClick={() => onNavigate('rfis')} />
        <KpiCard label="Pending Submittals" value={stats.pendingSubmittals} icon="📨" accent={stats.pendingSubmittals > 0 ? 'indigo' : 'default'} onClick={() => onNavigate('submittals')} />
        <KpiCard label="Photos" value={stats.photos} icon="📷" accent="blue" onClick={() => onNavigate('photos')} />
      </div>
      {(rfiData.length > 0 || submData.length > 0) && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {rfiData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">RFIs by Status</h3>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={rfiData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65}>
                    {rfiData.map((_, i) => <Cell key={i} fill={['#f59e0b','#60a5fa','#22c55e','#94a3b8'][i % 4]} />)}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          {submData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Submittals by Status</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={submData} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#818cf8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const DocumentsPage = () => {
  const [tab, setTab] = useState<Tab>('documents');
  const [search, setSearch] = useState('');
  const [rfiModal, setRfiModal] = useState<{ open: boolean; record?: RFI }>({ open: false });
  const [submModal, setSubmModal] = useState<{ open: boolean; record?: Submittal }>({ open: false });

  const tabs: { key: Tab; label: string }[] = [
    { key: 'documents', label: 'Documents' },
    { key: 'rfis', label: 'RFIs' },
    { key: 'submittals', label: 'Submittals' },
    { key: 'photos', label: 'Photos' },
  ];

  const handleNavigate = (t: Tab) => {
    setTab(t);
    setTimeout(() => document.getElementById('docs-list')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
        <div>
          {tab === 'rfis' && (
            <button
              type="button"
              onClick={() => setRfiModal({ open: true })}
              className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-600"
            >
              + New RFI
            </button>
          )}
          {tab === 'submittals' && (
            <button
              type="button"
              onClick={() => setSubmModal({ open: true })}
              className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-600"
            >
              + New Submittal
            </button>
          )}
        </div>
      </div>
      <DocumentsDashboard onNavigate={handleNavigate} />

      <div id="docs-list" className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
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

      <div className="mb-4">
        <input
          type="search"
          title="Search"
          placeholder={`Search ${tab}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      {tab === 'documents' && <DocumentsTable search={search} />}
      {tab === 'rfis' && (
        <RFIsTable
          search={search}
          onEdit={(rfi) => setRfiModal({ open: true, record: rfi })}
        />
      )}
      {tab === 'submittals' && (
        <SubmittalsTable
          search={search}
          onEdit={(sub) => setSubmModal({ open: true, record: sub })}
        />
      )}
      {tab === 'photos' && <PhotosGrid search={search} />}

      {rfiModal.open && (
        <RFIModal
          record={rfiModal.record}
          onClose={() => setRfiModal({ open: false })}
        />
      )}
      {submModal.open && (
        <SubmittalModal
          record={submModal.record}
          onClose={() => setSubmModal({ open: false })}
        />
      )}
    </div>
  );
};

/* ─── RFI Modal ─────────────────────────────────────────────── */
function RFIModal({ record, onClose }: { record?: RFI; onClose: () => void }) {
  const isEdit = !!record;
  const create = useCreateRFI();
  const update = useUpdateRFI();
  const { data: projects } = useProjects({ page_size: '100' });

  const [form, setForm] = useState({
    project: record?.project ?? '',
    subject: record?.subject ?? '',
    status: (record?.status ?? 'OPEN') as RFIStatus,
    question: record?.question ?? '',
    answer: record?.answer ?? '',
    due_date: record?.due_date ?? '',
  });

  useEffect(() => {
    setForm({
      project: record?.project ?? '',
      subject: record?.subject ?? '',
      status: (record?.status ?? 'OPEN') as RFIStatus,
      question: record?.question ?? '',
      answer: record?.answer ?? '',
      due_date: record?.due_date ?? '',
    });
  }, [record]);

  const busy = create.isPending || update.isPending;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      project: form.project,
      subject: form.subject,
      question: form.question,
    };
    if (form.status) payload.status = form.status;
    if (form.answer) payload.answer = form.answer;
    if (form.due_date) payload.due_date = form.due_date;

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit RFI' : 'New RFI'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Project *">
          <select
            title="Project"
            required
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            className={selectCls}
          >
            <option value="">— Select project —</option>
            {projects?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Subject *">
          <input
            title="Subject"
            required
            value={form.subject}
            onChange={(e) => setForm({ ...form, subject: e.target.value })}
            placeholder="Brief RFI subject"
            className={inputCls}
          />
        </Field>
        <Field label="Status">
          <select
            title="Status"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as RFIStatus })}
            className={selectCls}
          >
            <option value="DRAFT">Draft</option>
            <option value="OPEN">Open</option>
            <option value="ANSWERED">Answered</option>
            <option value="CLOSED">Closed</option>
          </select>
        </Field>
        <Field label="Question *">
          <textarea
            title="Question"
            required
            rows={3}
            value={form.question}
            onChange={(e) => setForm({ ...form, question: e.target.value })}
            placeholder="Describe the question or clarification needed"
            className={inputCls}
          />
        </Field>
        {(isEdit || form.status !== 'OPEN') && (
          <Field label="Answer">
            <textarea
              title="Answer"
              rows={3}
              value={form.answer}
              onChange={(e) => setForm({ ...form, answer: e.target.value })}
              placeholder="Response to the RFI"
              className={inputCls}
            />
          </Field>
        )}
        <Field label="Due Date">
          <input
            title="Due date"
            type="date"
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ─── Submittal Modal ───────────────────────────────────────── */
function SubmittalModal({ record, onClose }: { record?: Submittal; onClose: () => void }) {
  const isEdit = !!record;
  const create = useCreateSubmittal();
  const update = useUpdateSubmittal();
  const { data: projects } = useProjects({ page_size: '100' });

  const [form, setForm] = useState({
    project: record?.project ?? '',
    title: record?.title ?? '',
    spec_section: record?.spec_section ?? '',
    status: (record?.status ?? 'draft') as SubmittalStatus,
    submitted_date: record?.submitted_date ?? '',
    required_by: record?.required_by ?? '',
    review_notes: record?.review_notes ?? '',
  });

  useEffect(() => {
    setForm({
      project: record?.project ?? '',
      title: record?.title ?? '',
      spec_section: record?.spec_section ?? '',
      status: (record?.status ?? 'draft') as SubmittalStatus,
      submitted_date: record?.submitted_date ?? '',
      required_by: record?.required_by ?? '',
      review_notes: record?.review_notes ?? '',
    });
  }, [record]);

  const busy = create.isPending || update.isPending;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      title: form.title,
      status: form.status,
    };
    if (form.project) payload.project = form.project;
    if (form.spec_section) payload.spec_section = form.spec_section;
    if (form.submitted_date) payload.submitted_date = form.submitted_date;
    if (form.required_by) payload.required_by = form.required_by;
    if (form.review_notes) payload.review_notes = form.review_notes;

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit Submittal' : 'New Submittal'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Project">
          <select
            title="Project"
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            className={selectCls}
          >
            <option value="">— Select project —</option>
            {projects?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Title *">
          <input
            title="Title"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Submittal title"
            className={inputCls}
          />
        </Field>
        <Field label="Spec Section">
          <input
            title="Spec section"
            value={form.spec_section}
            onChange={(e) => setForm({ ...form, spec_section: e.target.value })}
            placeholder="e.g. 03 30 00"
            className={inputCls}
          />
        </Field>
        <Field label="Status">
          <select
            title="Status"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as SubmittalStatus })}
            className={selectCls}
          >
            <option value="draft">Draft</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="approved">Approved</option>
            <option value="approved_as_noted">Approved as Noted</option>
            <option value="rejected">Rejected</option>
            <option value="resubmit">Resubmit</option>
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Submitted Date">
            <input
              title="Submitted date"
              type="date"
              value={form.submitted_date}
              onChange={(e) => setForm({ ...form, submitted_date: e.target.value })}
              className={inputCls}
            />
          </Field>
          <Field label="Required By">
            <input
              title="Required by date"
              type="date"
              value={form.required_by}
              onChange={(e) => setForm({ ...form, required_by: e.target.value })}
              className={inputCls}
            />
          </Field>
        </div>
        <Field label="Review Notes">
          <textarea
            title="Review notes"
            rows={2}
            value={form.review_notes}
            onChange={(e) => setForm({ ...form, review_notes: e.target.value })}
            placeholder="Reviewer comments"
            className={inputCls}
          />
        </Field>
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ─── Tables ─────────────────────────────────────────────────── */
function DocumentsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20', is_current_version: 'true' };
  if (search) params.search = search;
  const { data, isLoading } = useDocuments(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Title</Th>
            <Th>Project</Th>
            <Th>Folder</Th>
            <Th>Type</Th>
            <Th>Version</Th>
            <Th>Uploaded By</Th>
            <Th>Date</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No documents found.</td></tr>
          )}
          {data?.results.map((doc) => (
            <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileIcon type={doc.content_type} />
                  <span className="font-medium text-slate-900">{doc.title}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-500 text-xs">{doc.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{doc.folder_name ?? '—'}</td>
              <td className="px-4 py-3">
                {doc.content_type && (
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs uppercase text-slate-600">
                    {doc.content_type.split('/').pop()}
                  </span>
                )}
              </td>
              <td className="px-4 py-3 text-center text-slate-500">v{doc.version}</td>
              <td className="px-4 py-3 text-slate-600">{doc.uploaded_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-500">
                {new Date(doc.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="documents" />
    </div>
  );
}

function RFIsTable({ search, onEdit }: { search: string; onEdit: (rfi: RFI) => void }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useRFIs(params);
  const deleteRFI = useDeleteRFI();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>RFI #</Th>
            <Th>Project</Th>
            <Th>Title</Th>
            <Th>Submitted By</Th>
            <Th>Due Date</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No RFIs found.</td></tr>
          )}
          {data?.results.map((rfi) => (
            <tr key={rfi.id} className={`group hover:bg-slate-50 transition-colors ${rfi.is_overdue ? 'bg-red-50/40' : ''}`}>
              <td className="px-4 py-3 font-medium text-slate-900">RFI-{String(rfi.rfi_number).padStart(3, '0')}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{rfi.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-900">
                {rfi.subject}
                {rfi.is_overdue && (
                  <span className="ml-2 rounded-full bg-red-100 px-1.5 py-0.5 text-xs text-red-600">Overdue</span>
                )}
              </td>
              <td className="px-4 py-3 text-slate-600">{rfi.requested_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {fmtDate(rfi.due_date)}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${RFI_STATUS_COLORS[rfi.status]}`}>
                  {rfi.status}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ActionBtn onClick={() => onEdit(rfi)}>Edit</ActionBtn>
                  <ActionBtn
                    danger
                    onClick={() => {
                      if (confirm(`Delete RFI "${rfi.title}"?`)) deleteRFI.mutate(rfi.id);
                    }}
                  >
                    Delete
                  </ActionBtn>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="RFIs" />
    </div>
  );
}

function SubmittalsTable({ search, onEdit }: { search: string; onEdit: (sub: Submittal) => void }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useSubmittals(params);
  const deleteSubmittal = useDeleteSubmittal();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>#</Th>
            <Th>Project</Th>
            <Th>Title</Th>
            <Th>Spec Section</Th>
            <Th>Submitted</Th>
            <Th>Required By</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-400">No submittals found.</td></tr>
          )}
          {data?.results.map((sub) => (
            <tr key={sub.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{String(sub.submittal_number).padStart(3, '0')}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{sub.project_name}</td>
              <td className="px-4 py-3 text-slate-900">{sub.title}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-500">{sub.spec_section ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {fmtDate(sub.submitted_date)}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {fmtDate(sub.required_by)}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SUBMITTAL_STATUS_COLORS[sub.status]}`}>
                  {sub.status.replace(/_/g, ' ')}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ActionBtn onClick={() => onEdit(sub)}>Edit</ActionBtn>
                  <ActionBtn
                    danger
                    onClick={() => {
                      if (confirm(`Delete submittal "${sub.title}"?`)) deleteSubmittal.mutate(sub.id);
                    }}
                  >
                    Delete
                  </ActionBtn>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="submittals" />
    </div>
  );
}

function PhotosGrid({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '24' };
  if (search) params.search = search;
  const { data, isLoading } = usePhotos(params);

  if (isLoading) return <Spinner />;
  return (
    <div>
      {data?.results.length === 0 && (
        <div className="flex h-40 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 text-sm">
          No photos found.
        </div>
      )}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {data?.results.map((photo) => (
          <a
            key={photo.id}
            href={photo.download_url ?? '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="group relative aspect-square overflow-hidden rounded-xl border border-slate-200 bg-slate-100"
          >
            {photo.thumbnail_url ? (
              <img
                src={photo.thumbnail_url}
                alt={photo.caption ?? 'Site photo'}
                className="h-full w-full object-cover transition-transform group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-slate-300">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
            )}
            {photo.caption && (
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                <p className="text-xs text-white line-clamp-2">{photo.caption}</p>
              </div>
            )}
          </a>
        ))}
      </div>
      <Pagination count={data?.count} shown={data?.results.length} label="photos" />
    </div>
  );
}

/* ─── Shared UI Primitives ───────────────────────────────────── */
function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button type="button" title="Close" onClick={onClose} className="rounded p-1 text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-6 py-4">{children}</div>
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
      <button type="button" onClick={onClose} className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
        Cancel
      </button>
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-50"
      >
        {busy ? 'Saving…' : isEdit ? 'Save Changes' : 'Create'}
      </button>
    </div>
  );
}

function ActionBtn({ children, onClick, danger }: { children: React.ReactNode; onClick: () => void; danger?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
        danger
          ? 'text-red-600 hover:bg-red-50'
          : 'text-blue-700 hover:bg-blue-50'
      }`}
    >
      {children}
    </button>
  );
}

function FileIcon({ type }: { type: string | null }) {
  const MIME_EXT: Record<string, string> = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'doc',
    'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif', 'image/webp': 'webp',
  };
  const colors: Record<string, string> = {
    pdf: 'text-red-500', xlsx: 'text-green-600', xls: 'text-green-600',
    docx: 'text-blue-600', doc: 'text-blue-600', jpg: 'text-blue-500',
    jpeg: 'text-blue-500', png: 'text-blue-500', gif: 'text-blue-500', webp: 'text-blue-500',
  };
  const ext = type ? (MIME_EXT[type] ?? type.split('/').pop() ?? '') : '';
  const color = colors[ext.toLowerCase()] ?? 'text-slate-400';
  return (
    <svg className={`h-4 w-4 flex-shrink-0 ${color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
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

const inputCls = 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400';
const selectCls = 'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400';
