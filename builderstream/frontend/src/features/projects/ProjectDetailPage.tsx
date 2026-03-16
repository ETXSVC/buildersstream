import { useState, useRef } from 'react';
import { fmtDate } from '@/utils/date';
import { useParams, Link } from 'react-router-dom';
import { useProject, useUpdateProjectStatus, useUpdateProject } from '@/hooks/useProjects';
import { useDocuments, useUploadDocument, useDeleteDocument } from '@/hooks/useDocuments';
import { fetchDocumentDownloadUrl } from '@/api/documents';
import type { ProjectStatus } from '@/types/projects';
import type { Document } from '@/types/documents';
import { STATUS_LABELS, STATUS_COLORS, HEALTH_COLORS } from '@/types/projects';
import { ProjectComments } from './ProjectComments';

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
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
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
        <Link to="/projects" className="hover:text-amber-600">Projects</Link>
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
                      className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-amber-50 first:rounded-t-lg last:rounded-b-lg"
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
          className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-5"
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
          <h3 className="mb-4 text-sm font-semibold text-amber-800">Edit Project</h3>

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
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium text-slate-600">Description</label>
              <textarea
                name="description"
                rows={3}
                defaultValue={project.description ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
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
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Start Date</label>
              <input
                name="start_date"
                type="date"
                defaultValue={project.start_date ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Target Completion</label>
              <input
                name="estimated_completion"
                type="date"
                defaultValue={project.estimated_completion ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Actual Completion</label>
              <input
                name="actual_completion"
                type="date"
                defaultValue={project.actual_completion ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium text-slate-600">Address</label>
              <input
                name="address"
                defaultValue={project.address ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">City</label>
              <input
                name="city"
                defaultValue={project.city ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">State</label>
              <input
                name="state"
                defaultValue={project.state ?? ''}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <button
              type="submit"
              disabled={updateProject.isPending}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
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
                ? 'border-b-2 border-amber-500 text-amber-700'
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
        <div className="space-y-3">
          {(!project.milestones || project.milestones.length === 0) ? (
            <p className="text-sm text-slate-400">No milestones yet.</p>
          ) : (
            project.milestones.map((m) => (
              <div key={m.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${
                    m.status === 'completed' ? 'bg-green-500' : m.is_overdue ? 'bg-red-500' : 'bg-amber-400'
                  }`} />
                  <span className="text-sm font-medium text-slate-900">{m.name}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  {m.due_date && <span>Due {fmtDate(m.due_date)}</span>}
                  {m.is_overdue && <span className="text-red-500 font-medium">Overdue</span>}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'team' && (
        <div className="space-y-3">
          {(!project.team || project.team.length === 0) ? (
            <p className="text-sm text-slate-400">No team members assigned.</p>
          ) : (
            project.team.map((member) => (
              <div key={member.user_id} className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100 text-amber-700 font-semibold text-sm">
                  {member.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">{member.name}</p>
                  <p className="text-xs text-slate-500">{member.email}</p>
                </div>
                <span className="ml-auto text-xs text-slate-400 capitalize">{member.role}</span>
              </div>
            ))
          )}
        </div>
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
          className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-600"
        >
          + Upload Document
        </button>
      </div>

      {isLoading && (
        <div className="flex h-24 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      )}

      {!isLoading && docs.length === 0 && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 py-12 text-center">
          <p className="text-sm text-slate-400">No documents attached to this project yet.</p>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="mt-3 text-sm font-medium text-amber-600 hover:text-amber-700"
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
                        className="text-xs font-medium text-amber-600 hover:text-amber-700"
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
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">File *</label>
                <input
                  ref={fileRef}
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-amber-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-amber-700 hover:file:bg-amber-100"
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
                className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
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
