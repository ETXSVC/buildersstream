import { useState, useRef, useEffect } from 'react';
import Gantt from 'frappe-gantt';
import { fmtDate } from '@/utils/date';
import { useParams, Link } from 'react-router-dom';
import { useProject, useUpdateProjectStatus, useUpdateProject } from '@/hooks/useProjects';
import { useDocuments, useUploadDocument, useDeleteDocument } from '@/hooks/useDocuments';
import { fetchDocumentDownloadUrl } from '@/api/documents';
import type { ProjectStatus } from '@/types/projects';
import type { Document } from '@/types/documents';
import { STATUS_LABELS, STATUS_COLORS, HEALTH_COLORS } from '@/types/projects';
import { ProjectComments } from './ProjectComments';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';

type Tab = 'overview' | 'milestones' | 'team' | 'comments' | 'documents';

const VALID_TRANSITIONS: Record<ProjectStatus, ProjectStatus[]> = {
  prospect:       ['site_survey', 'canceled'],
  site_survey:    ['proposal', 'prospect', 'canceled'],
  proposal:       ['acceptance', 'site_survey', 'canceled'],
  acceptance:     ['in_progress', 'proposal', 'canceled'],
  in_progress:    ['milestones', 'canceled'],
  milestones:     ['finish_project', 'in_progress', 'canceled'],
  finish_project: ['billing', 'milestones', 'canceled'],
  billing:        ['paid_complete', 'finish_project'],
  paid_complete:  [],
  canceled:       ['prospect'],
};

export const ProjectDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading, error } = useProject(id ?? '');
  const [tab, setTab] = useState<Tab>('overview');
  const [statusMenuOpen, setStatusMenuOpen] = useState(false);
  const [transitionError, setTransitionError] = useState('');
  const [editing, setEditing] = useState(false);
  const [editError, setEditError] = useState('');
  const updateStatus = useUpdateProjectStatus();
  const updateProject = useUpdateProject();

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load project.
        </div>
      </div>
    );
  }

  const nextStatuses = VALID_TRANSITIONS[project.status] ?? [];

  const handleTransition = (new_status: ProjectStatus) => {
    setStatusMenuOpen(false);
    setTransitionError('');
    updateStatus.mutate(
      { id: project.id, new_status },
      {
        onError: (err: unknown) => {
          const msg =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            ?? 'Failed to change status.';
          setTransitionError(msg);
        },
      },
    );
  };

  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <div className="mb-4 flex items-center gap-2 text-sm text-slate-500">
        <Link to="/projects" className="hover:text-blue-600">Projects</Link>
        <span>/</span>
        <span className="text-slate-900">{project.name}</span>
      </div>

      {/* Header */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">{project.name}</h1>
            {project.health_status && (
              <span className={`h-3 w-3 rounded-full ${HEALTH_COLORS[project.health_status]}`} />
            )}
          </div>
          <p className="mt-1 text-sm text-slate-500">{project.project_number}</p>
        </div>

        {/* Edit button + Status badge + transition dropdown */}
        <div className="relative flex items-center gap-2">
          <button
            type="button"
            onClick={() => { setEditing((e) => !e); setEditError(''); }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            {editing ? 'Cancel' : 'Edit Project'}
          </button>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${STATUS_COLORS[project.status]}`}>
            {STATUS_LABELS[project.status]}
          </span>
          {nextStatuses.length > 0 && (
            <div className="relative">
              <button
                type="button"
                onClick={() => setStatusMenuOpen((o) => !o)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 focus:outline-none"
                disabled={updateStatus.isPending}
              >
                {updateStatus.isPending ? 'Updating…' : 'Move to →'}
              </button>
              {statusMenuOpen && (
                <div className="absolute right-0 top-full z-20 mt-1 w-44 rounded-lg border border-slate-200 bg-white shadow-lg">
                  {nextStatuses.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => handleTransition(s)}
                      className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-blue-50 first:rounded-t-lg last:rounded-b-lg"
                    >
                      {STATUS_LABELS[s]}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Transition error */}
      {transitionError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {transitionError}
        </div>
      )}

      {/* Inline edit form */}
      {editing && (
        <form
          className="mb-6 rounded-xl border border-blue-200 bg-blue-50 p-5"
          onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            const payload: Record<string, string | null> = {
              name: (fd.get('name') as string).trim(),
              // Text fields: blank=True but NOT null=True — must send '' not null
              description: (fd.get('description') as string).trim(),
              address: (fd.get('address') as string).trim(),
              city: (fd.get('city') as string).trim(),
              state: (fd.get('state') as string).trim(),
              // Nullable fields: null=True blank=True — null OK for empty
              estimated_value: (fd.get('estimated_value') as string).trim() || null,
              start_date: (fd.get('start_date') as string) || null,
              estimated_completion: (fd.get('estimated_completion') as string) || null,
              actual_completion: (fd.get('actual_completion') as string) || null,
            };
            setEditError('');
            updateProject.mutate(
              { id: project.id, payload },
              {
                onSuccess: () => setEditing(false),
                onError: (err: unknown) => {
                  const data = (err as { response?: { data?: Record<string, unknown> } })?.response?.data;
                  let msg = 'Failed to save changes.';
                  if (data) {
                    if (typeof data.detail === 'string') {
                      msg = data.detail;
                    } else {
                      const fieldErrors = Object.entries(data)
                        .map(([field, errors]) => {
                          const label = field.replace(/_/g, ' ');
                          const errText = Array.isArray(errors) ? errors.join(' ') : String(errors);
                          return `${label}: ${errText}`;
                        })
                        .join('  •  ');
                      if (fieldErrors) msg = fieldErrors;
                    }
                  }
                  setEditError(msg);
                },
              },
            );
          }}
        >
          <h3 className="mb-4 text-sm font-semibold text-blue-800">Edit Project</h3>

          {editError && (
            <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
              {editError}
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium text-slate-600">Project Name *</label>
              <input
                name="name"
                required
                defaultValue={project.name}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium text-slate-600">Description</label>
              <textarea
                name="description"
                rows={3}
                defaultValue={project.description ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Estimated Value ($)</label>
              <input
                name="estimated_value"
                type="number"
                min="0"
                step="0.01"
                defaultValue={project.estimated_value ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Start Date</label>
              <input
                name="start_date"
                type="date"
                defaultValue={project.start_date ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Target Completion</label>
              <input
                name="estimated_completion"
                type="date"
                defaultValue={project.estimated_completion ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Actual Completion</label>
              <input
                name="actual_completion"
                type="date"
                defaultValue={project.actual_completion ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium text-slate-600">Address</label>
              <input
                name="address"
                defaultValue={project.address ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">City</label>
              <input
                name="city"
                defaultValue={project.city ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">State</label>
              <input
                name="state"
                defaultValue={project.state ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <button
              type="submit"
              disabled={updateProject.isPending}
              className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
            >
              {updateProject.isPending ? 'Saving…' : 'Save Changes'}
            </button>
            <button
              type="button"
              onClick={() => { setEditing(false); setEditError(''); }}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Stat cards */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Contract Value" value={project.estimated_value
          ? `$${Number(project.estimated_value).toLocaleString()}`
          : '—'} />
        <StatCard label="Health Score" value={project.health_score !== null ? `${project.health_score}/100` : '—'} />
        <StatCard label="Start Date" value={fmtDate(project.start_date)} />
        <StatCard label="Target Completion" value={fmtDate(project.estimated_completion)} />
      </div>

      {/* Tabs */}
      <div className="mb-6 flex border-b border-slate-200">
        {(['overview', 'milestones', 'team', 'comments', 'documents'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={[
              'px-4 py-2 text-sm font-medium capitalize transition-colors',
              tab === t
                ? 'border-b-2 border-blue-500 text-blue-700'
                : 'text-slate-500 hover:text-slate-700',
            ].join(' ')}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <InfoBlock title="Project Details">
            <InfoRow label="Client" value={project.client_name ?? '—'} />
            <InfoRow label="Project Manager" value={project.project_manager_name ?? '—'} />
            <InfoRow label="Address" value={[project.address, project.city, project.state].filter(Boolean).join(', ') || '—'} />
            <InfoRow label="Status" value={STATUS_LABELS[project.status]} />
          </InfoBlock>
          {project.description && (
            <InfoBlock title="Description">
              <p className="text-sm text-slate-600">{project.description}</p>
            </InfoBlock>
          )}
          <InfoBlock title="Activity">
            <div className="space-y-2">
              <InfoRow label="Open Action Items" value={String(project.action_items_count ?? 0)} />
              <InfoRow label="Open RFIs" value={String(project.open_rfis_count ?? 0)} />
              <InfoRow label="Pending Submittals" value={String(project.pending_submittals_count ?? 0)} />
            </div>
          </InfoBlock>
        </div>
      )}

      {tab === 'milestones' && (
        <MilestonesTab project={project} initialMilestones={project.milestones} />
      )}

      {tab === 'team' && (
        <TeamTab projectId={project.id} />
      )}

      {tab === 'comments' && (
        <div className="max-w-2xl rounded-xl border border-slate-200 bg-slate-50 p-5">
          <ProjectComments projectId={project.id} />
        </div>
      )}

      {tab === 'documents' && (
        <ProjectDocumentsTab projectId={project.id} />
      )}
    </div>
  );
};

function ProjectDocumentsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useDocuments({ project: projectId });
  const upload = useUploadDocument(projectId);
  const remove = useDeleteDocument();
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const docs: Document[] = data?.results ?? [];

  const handleUpload = () => {
    if (!file || !title.trim()) return;
    setUploadError('');
    upload.mutate(
      { file, title: title.trim() },
      {
        onSuccess: () => {
          setModalOpen(false);
          setTitle('');
          setFile(null);
        },
        onError: () => setUploadError('Upload failed. Check that AWS S3 is configured in .env'),
      },
    );
  };

  const handleDownload = async (doc: Document) => {
    try {
      const { download_url } = await fetchDocumentDownloadUrl(doc.id);
      const res = await fetch(download_url, { credentials: 'include' });
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = doc.file_name;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch {
      alert('Could not download file.');
    }
  };

  const handleDelete = (doc: Document) => {
    if (!confirm(`Delete "${doc.title}"?`)) return;
    remove.mutate(doc.id);
  };

  function fmtSize(bytes: number | null) {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-slate-500">{docs.length} document{docs.length !== 1 ? 's' : ''}</p>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-600"
        >
          + Upload Document
        </button>
      </div>

      {isLoading && (
        <div className="flex h-24 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {!isLoading && docs.length === 0 && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 py-12 text-center">
          <p className="text-sm text-slate-400">No documents attached to this project yet.</p>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Upload the first document
          </button>
        </div>
      )}

      {docs.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Title</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">File</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Uploaded by</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Date</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {docs.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{doc.title}</td>
                  <td className="px-4 py-3 text-slate-500">{doc.file_name}</td>
                  <td className="px-4 py-3 text-slate-500">{fmtSize(doc.file_size)}</td>
                  <td className="px-4 py-3 text-slate-500">{doc.uploaded_by_name ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-500">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => handleDownload(doc)}
                        className="text-xs font-medium text-blue-600 hover:text-blue-700"
                      >
                        Download
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(doc)}
                        className="text-xs font-medium text-red-500 hover:text-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-base font-semibold text-slate-900">Upload Document</h2>

            {uploadError && (
              <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                {uploadError}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Signed Contract"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">File *</label>
                <input
                  ref={fileRef}
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => { setModalOpen(false); setTitle(''); setFile(null); setUploadError(''); }}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUpload}
                disabled={!file || !title.trim() || upload.isPending}
                className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-50"
              >
                {upload.isPending ? 'Uploading…' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function InfoBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-slate-900">{value}</span>
    </div>
  );
}

function MilestonesTab({ project, initialMilestones }: { project: any; initialMilestones: any[] }) {
  const projectId = project.id;
  const qc = useQueryClient();
  const ganttRef = useRef<HTMLDivElement>(null);
  const ganttInstance = useRef<any>(null);
  const [viewMode, setViewMode] = useState<'Day' | 'Week' | 'Month'>('Month');
  const [addingName, setAddingName] = useState('');
  const [addingDate, setAddingDate] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const { data: milestones } = useQuery({
    queryKey: ['project-milestones', projectId],
    queryFn: () => apiClient.get(`/api/v1/projects/${projectId}/milestones/`).then(r => r.data),
    initialData: initialMilestones,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ['project-milestones', projectId] });

  const toggle = useMutation({
    mutationFn: ({ id, is_completed }: { id: string; is_completed: boolean }) =>
      apiClient.patch(`/api/v1/projects/${projectId}/milestones/${id}/`, { is_completed }),
    onSuccess: invalidate,
  });

  const patchDue = useMutation({
    mutationFn: ({ id, due_date }: { id: string; due_date: string }) =>
      apiClient.patch(`/api/v1/projects/${projectId}/milestones/${id}/`, { due_date }),
    onSuccess: invalidate,
  });

  const deleteMilestone = useMutation({
    mutationFn: (id: string) =>
      apiClient.delete(`/api/v1/projects/${projectId}/milestones/${id}/`),
    onSuccess: invalidate,
  });

  const addMilestone = useMutation({
    mutationFn: () =>
      apiClient.post(`/api/v1/projects/${projectId}/milestones/`, {
        name: addingName,
        due_date: addingDate || null,
      }),
    onSuccess: () => { invalidate(); setAddingName(''); setAddingDate(''); setShowAdd(false); },
  });

  // Stable ref so on_date_change closure never goes stale
  const patchDueRef = useRef(patchDue.mutate);
  useEffect(() => { patchDueRef.current = patchDue.mutate; });

  // Local date string without UTC shift (toISOString shifts by timezone)
  const toLocalDate = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

  // Build + render Gantt whenever milestones changes
  useEffect(() => {
    if (!ganttRef.current) return;
    const withDates = (milestones ?? []).filter((m: any) => m.due_date);
    if (!withDates.length) return;

    // Each milestone = 14-day bar ending on due_date (gives each its own position on the timeline)
    const tasks = withDates.map((m: any) => {
      const due = new Date(m.due_date + 'T12:00:00'); // noon to avoid DST edge cases
      const start = new Date(due);
      start.setDate(start.getDate() - 13);
      return {
        id: m.id,
        name: m.name,
        start: toLocalDate(start),
        end: m.due_date,
        progress: m.is_completed ? 100 : 0,
        custom_class: m.is_completed ? 'milestone-done' : m.is_overdue ? 'milestone-overdue' : 'milestone-upcoming',
      };
    });

    ganttRef.current.innerHTML = '';
    ganttInstance.current = new Gantt(ganttRef.current, tasks, {
      view_mode: viewMode,
      date_format: 'YYYY-MM-DD',
      popup_trigger: 'click',
      on_date_change: (task: any, _start: Date, end: Date) => {
        patchDueRef.current({ id: task.id, due_date: toLocalDate(end) });
      },
      on_progress_change: () => {},
      on_click: () => {},
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [milestones]);

  // Switch view mode on existing instance (no rebuild needed)
  useEffect(() => {
    if (!ganttInstance.current) return;
    ganttInstance.current.change_view_mode(viewMode);
  }, [viewMode]);

  const withDates = (milestones ?? []).filter((m: any) => m.due_date);
  const noDates = (milestones ?? []).filter((m: any) => !m.due_date);

  return (
    <div className="space-y-4">
      {/* Gantt toolbar */}
      {withDates.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="flex rounded-lg border border-slate-200 bg-white overflow-hidden text-sm">
            {(['Day', 'Week', 'Month'] as const).map(m => (
              <button key={m} type="button" onClick={() => setViewMode(m)}
                className={`px-3 py-1.5 font-medium transition-colors ${viewMode === m ? 'bg-blue-500 text-white' : 'text-slate-600 hover:bg-slate-50'}`}>
                {m}
              </button>
            ))}
          </div>
          <span className="text-xs text-slate-400">Drag bars to change due dates</span>
        </div>
      )}

      {/* Gantt chart */}
      {withDates.length > 0 ? (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <style>{`
            .milestone-done .bar { fill: #22c55e !important; }
            .milestone-overdue .bar { fill: #ef4444 !important; }
            .milestone-upcoming .bar { fill: #3b82f6 !important; }
            .gantt .bar-label { fill: #fff !important; font-size: 11px !important; }
            .gantt-container { font-family: inherit !important; }
          `}</style>
          <div ref={ganttRef} className="p-2" />
        </div>
      ) : (
        !showAdd && <p className="text-sm text-slate-400">Add milestones with due dates to see the Gantt chart.</p>
      )}

      {/* Milestone rows (below chart — complete / delete / dates) */}
      <div className="space-y-2">
        {(milestones ?? []).map((m: any) => (
          <div key={m.id} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3">
            <button type="button"
              onClick={() => toggle.mutate({ id: m.id, is_completed: !m.is_completed })}
              className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                m.is_completed ? 'border-green-500 bg-green-500 text-white' : 'border-slate-300 hover:border-green-400'
              }`}>
              {m.is_completed && (
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>

            <span className={`flex-1 text-sm font-medium ${m.is_completed ? 'text-slate-400 line-through' : 'text-slate-900'}`}>
              {m.name}
            </span>

            <input type="date" defaultValue={m.due_date ?? ''}
              onBlur={(e) => { if (e.target.value !== (m.due_date ?? '')) patchDue.mutate({ id: m.id, due_date: e.target.value }); }}
              className="rounded border border-slate-200 px-2 py-1 text-xs text-slate-500 focus:border-blue-400 focus:outline-none" />

            {m.is_overdue && !m.is_completed && (
              <span className="text-xs font-medium text-red-500">Overdue</span>
            )}

            <button type="button" onClick={() => deleteMilestone.mutate(m.id)}
              disabled={deleteMilestone.isPending}
              className="text-slate-200 hover:text-red-400 transition-colors">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}

        {noDates.length > 0 && withDates.length > 0 && (
          <p className="text-xs text-slate-400 pl-1">↑ Set due dates on the rows above to show them in the chart.</p>
        )}
      </div>

      {/* Add milestone */}
      {showAdd ? (
        <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
          <input type="text" placeholder="Milestone name…" value={addingName}
            onChange={e => setAddingName(e.target.value)}
            className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <input type="date" value={addingDate} onChange={e => setAddingDate(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="button" disabled={!addingName.trim() || addMilestone.isPending}
            onClick={() => addMilestone.mutate()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
            Add
          </button>
          <button type="button" onClick={() => setShowAdd(false)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 hover:bg-slate-50">
            Cancel
          </button>
        </div>
      ) : (
        <button type="button" onClick={() => setShowAdd(true)}
          className="flex items-center gap-1.5 rounded-lg border border-dashed border-slate-300 px-4 py-2 text-sm font-medium text-slate-500 hover:border-blue-400 hover:text-blue-600 transition-colors">
          <span className="text-lg leading-none">+</span> Add Milestone
        </button>
      )}
    </div>
  );
}

const MEMBER_ROLES = ['member', 'lead', 'foreman', 'superintendent', 'safety_officer', 'estimator'];

function initials(name: string) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

function TeamTab({ projectId }: { projectId: string }) {
  const qc = useQueryClient();
  const [empId, setEmpId] = useState('');
  const [role, setRole] = useState('member');
  const [adding, setAdding] = useState(false);
  const [teamId, setTeamId] = useState('');
  const [changingTeam, setChangingTeam] = useState(false);

  // All org teams — for the "assign crew team" dropdown
  const { data: teamsData } = useQuery({
    queryKey: ['org-teams'],
    queryFn: () => apiClient.get('/api/v1/teams/').then(r => r.data?.results ?? r.data),
  });

  // All employees — for the "add member" dropdown
  const { data: employeesData } = useQuery({
    queryKey: ['org-employees'],
    queryFn: () => apiClient.get('/api/v1/payroll/employees/?is_active=true&page_size=500').then(r => r.data?.results ?? r.data),
  });

  // Current project (to read project.team / project.team_name)
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.get(`/api/v1/projects/${projectId}/`).then(r => r.data),
  });

  const assignTeam = useMutation({
    mutationFn: (tid: string | null) =>
      apiClient.patch(`/api/v1/projects/${projectId}/`, { team: tid }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['project', projectId] });
      qc.invalidateQueries({ queryKey: ['org-teams'] });
      setChangingTeam(false);
      setTeamId('');
    },
  });

  const addEmployee = useMutation({
    mutationFn: ({ tid, eid, r }: { tid: string; eid: string; r: string }) =>
      apiClient.post(`/api/v1/teams/${tid}/add-member/`, { employee_id: eid, role: r }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['org-teams'] });
      setEmpId('');
      setAdding(false);
    },
  });

  const removeEmployee = useMutation({
    mutationFn: ({ tid, eid }: { tid: string; eid: string }) =>
      apiClient.delete(`/api/v1/teams/${tid}/remove-member/${eid}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['org-teams'] }),
  });

  const teams: any[] = teamsData ?? [];
  const employees: any[] = employeesData ?? [];

  // Find the full team object (includes members[] with employees)
  const assignedTeam = project?.team
    ? teams.find((t: any) => t.id === project.team)
    : null;

  const existingEmpIds = new Set((assignedTeam?.members ?? []).map((m: any) => m.employee));
  const availableEmps = employees.filter((e: any) => !existingEmpIds.has(e.id));

  return (
    <div className="space-y-4">
      {/* ── Team assignment ── */}
      <div className="flex items-center justify-between">
        <div>
          {project?.team ? (
            <span className="text-sm font-medium text-slate-900">{project.team_name}</span>
          ) : (
            <span className="text-sm text-slate-400">No team assigned</span>
          )}
        </div>
        {!changingTeam && (
          <button type="button" onClick={() => { setChangingTeam(true); setTeamId(project?.team ?? ''); }}
            className="text-xs text-blue-600 hover:underline">
            {project?.team ? 'Change team' : 'Assign team'}
          </button>
        )}
      </div>

      {changingTeam && (
        <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
          <select value={teamId} onChange={e => setTeamId(e.target.value)}
            className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">— No team —</option>
            {teams.map((t: any) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <button type="button" disabled={assignTeam.isPending}
            onClick={() => assignTeam.mutate(teamId || null)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
            Save
          </button>
          <button type="button" onClick={() => setChangingTeam(false)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 hover:bg-slate-50">
            Cancel
          </button>
        </div>
      )}

      {/* ── Employee / contractor list ── */}
      {project?.team && (
        <>
          {adding ? (
            <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
              <select value={empId} onChange={e => setEmpId(e.target.value)}
                className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Select employee / contractor…</option>
                {availableEmps.map((e: any) => (
                  <option key={e.id} value={e.id}>
                    {e.full_name || `${e.first_name} ${e.last_name}`}
                    {e.employment_type === 'contractor' ? ' (contractor)' : ''}
                    {e.trade ? ` — ${e.trade}` : ''}
                  </option>
                ))}
              </select>
              <select value={role} onChange={e => setRole(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {MEMBER_ROLES.map(r => <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>)}
              </select>
              <button type="button" disabled={!empId || addEmployee.isPending}
                onClick={() => addEmployee.mutate({ tid: project.team, eid: empId, r: role })}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                Add
              </button>
              <button type="button" onClick={() => setAdding(false)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 hover:bg-slate-50">
                Cancel
              </button>
            </div>
          ) : (
            <button type="button" onClick={() => setAdding(true)}
              className="flex items-center gap-1.5 rounded-lg border border-dashed border-slate-300 px-4 py-2 text-sm font-medium text-slate-500 hover:border-blue-400 hover:text-blue-600 transition-colors">
              <span className="text-lg leading-none">+</span> Add Employee / Contractor
            </button>
          )}

          <div className="mt-3 space-y-2">
            {(assignedTeam?.members ?? []).length === 0 && !adding && (
              <p className="text-sm text-slate-400">No members in this team yet.</p>
            )}
            {(assignedTeam?.members ?? []).map((m: any) => (
              <div key={m.id} className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold text-sm">
                  {initials(m.employee_name || '?')}
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">{m.employee_name}</p>
                  <p className="text-xs text-slate-500 capitalize">
                    {m.role?.replace(/_/g, ' ')}
                    {m.employee_trade ? ` · ${m.employee_trade}` : ''}
                  </p>
                </div>
                <button type="button"
                  onClick={() => removeEmployee.mutate({ tid: project.team, eid: m.employee })}
                  disabled={removeEmployee.isPending}
                  className="ml-auto text-xs text-slate-300 hover:text-red-400 transition-colors disabled:opacity-50">
                  Remove
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {!project?.team && !changingTeam && (
        <p className="text-sm text-slate-400">Assign a team above to manage employees and contractors.</p>
      )}
    </div>
  );
}
