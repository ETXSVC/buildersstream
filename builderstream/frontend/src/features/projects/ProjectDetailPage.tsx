import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useProject } from '@/hooks/useProjects';
import { STATUS_LABELS, STATUS_COLORS, HEALTH_COLORS } from '@/types/projects';

type Tab = 'overview' | 'milestones' | 'team';

export const ProjectDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading, error } = useProject(id ?? '');
  const [tab, setTab] = useState<Tab>('overview');

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
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${STATUS_COLORS[project.status]}`}>
          {STATUS_LABELS[project.status]}
        </span>
      </div>

      {/* Stat cards */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Contract Value" value={project.estimated_value
          ? `$${Number(project.estimated_value).toLocaleString()}`
          : '—'} />
        <StatCard label="Health Score" value={project.health_score !== null ? `${project.health_score}/100` : '—'} />
        <StatCard label="Start Date" value={project.start_date
          ? new Date(project.start_date).toLocaleDateString() : '—'} />
        <StatCard label="Target Completion" value={project.target_completion
          ? new Date(project.target_completion).toLocaleDateString() : '—'} />
      </div>

      {/* Tabs */}
      <div className="mb-6 flex border-b border-slate-200">
        {(['overview', 'milestones', 'team'] as Tab[]).map((t) => (
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
                  {m.due_date && <span>Due {new Date(m.due_date).toLocaleDateString()}</span>}
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
    </div>
  );
};

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
