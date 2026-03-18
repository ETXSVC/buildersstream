import { useState, useMemo } from 'react';
import { fmtDate } from '@/utils/date';
import { Link } from 'react-router-dom';
import { SubNav } from '@/components/SubNav';
const SUBNAV = [{ label: 'Projects', to: '/projects' }, { label: 'Scheduling', to: '/scheduling' }, { label: 'Documents', to: '/documents' }];
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  useProjects,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
} from '@/hooks/useProjects';
import { useContacts } from '@/hooks/useCRM';
import { useQuery } from '@tanstack/react-query';
import { fetchTeams } from '@/api/teams';
import type { Project, ProjectStatus, HealthStatus, ProjectFilters } from '@/types/projects';
import { STATUS_LABELS, STATUS_COLORS, HEALTH_COLORS } from '@/types/projects';

const STATUS_OPTIONS: { value: ProjectStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'prospect', label: 'Prospect' },
  { value: 'site_survey', label: 'Site Survey' },
  { value: 'proposal', label: 'Proposal' },
  { value: 'acceptance', label: 'Acceptance' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'milestones', label: 'Milestones' },
  { value: 'finish_project', label: 'Finish Project' },
  { value: 'billing', label: 'Billing' },
  { value: 'paid_complete', label: 'Paid / Complete' },
  { value: 'canceled', label: 'Canceled' },
];

const PROJECT_TYPE_OPTIONS = [
  { value: '', label: '— Select type —' },
  { value: 'residential_remodel', label: 'Residential Remodel' },
  { value: 'kitchen_bath', label: 'Kitchen & Bath' },
  { value: 'addition', label: 'Addition' },
  { value: 'new_home', label: 'New Home' },
  { value: 'commercial_buildout', label: 'Commercial Buildout' },
  { value: 'commercial_renovation', label: 'Commercial Renovation' },
  { value: 'roofing', label: 'Roofing' },
  { value: 'exterior', label: 'Exterior' },
  { value: 'specialty', label: 'Specialty' },
];

export const ProjectsPage = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | ''>('');
  const [healthFilter, setHealthFilter] = useState<HealthStatus | ''>('');
  const [editProject, setEditProject] = useState<Project | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  const scrollToFilters = () =>
    setTimeout(() => document.getElementById('projects-filters')?.scrollIntoView({ behavior: 'smooth' }), 50);

  const filters: ProjectFilters = {};
  if (search) filters.search = search;
  if (statusFilter) filters.status = statusFilter;
  if (healthFilter) filters.health_status = healthFilter;

  const { data, isLoading, error } = useProjects(filters);
  const allProjects = useProjects({});
  const deleteProject = useDeleteProject();

  const stats = useMemo(() => {
    const projects = allProjects.data?.results ?? [];
    const total = projects.length;
    const active = projects.filter(p => ['in_progress', 'milestones', 'finish_project'].includes(p.status)).length;
    const totalValue = projects.reduce((s, p) => s + parseFloat(p.estimated_value ?? '0'), 0);
    const green = projects.filter(p => p.health_status === 'green').length;
    const yellow = projects.filter(p => p.health_status === 'yellow').length;
    const red = projects.filter(p => p.health_status === 'red').length;
    const statusCounts = projects.reduce<Record<string, number>>((acc, p) => {
      acc[p.status] = (acc[p.status] ?? 0) + 1;
      return acc;
    }, {});
    return { total, active, totalValue, green, yellow, red, statusCounts };
  }, [allProjects.data]);

  const statusChartData = Object.entries(stats.statusCounts).map(([k, v]) => ({
    name: STATUS_LABELS[k as ProjectStatus] ?? k,
    count: v,
  }));
  const healthData = [
    { name: 'Green', value: stats.green, color: '#22c55e' },
    { name: 'Yellow', value: stats.yellow, color: '#f59e0b' },
    { name: 'Red', value: stats.red, color: '#ef4444' },
  ].filter(d => d.value > 0);

  return (
    <div className="p-6">
      <SubNav items={SUBNAV} />
      {/* Dashboard */}
      <div className="mb-8">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
          <KpiCard label="Total Projects" value={stats.total} icon="🏗️" onClick={() => { setStatusFilter(''); setHealthFilter(''); scrollToFilters(); }} />
          <KpiCard label="Active" value={stats.active} icon="⚡" accent="blue" onClick={() => { setStatusFilter('in_progress' as ProjectStatus); setHealthFilter(''); scrollToFilters(); }} />
          <KpiCard label="Pipeline Value" value={`$${(stats.totalValue / 1000).toFixed(0)}k`} icon="💰" accent="green" onClick={() => { setStatusFilter(''); setHealthFilter(''); scrollToFilters(); }} />
          <KpiCard label="Health: Red" value={stats.red} icon="🔴" accent={stats.red > 0 ? 'red' : 'default'} sub={`${stats.green} green · ${stats.yellow} yellow`} onClick={() => { setStatusFilter(''); setHealthFilter('red' as HealthStatus); scrollToFilters(); }} />
        </div>
        {(statusChartData.length > 0 || healthData.length > 0) && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Projects by Status</h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={statusChartData} margin={{ top: 0, right: 8, left: -20, bottom: 40 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Health Distribution</h3>
              {healthData.length > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={healthData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                      {healthData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                    </Pie>
                    <Legend />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-[180px] items-center justify-center text-sm text-slate-400">No health data yet</div>
              )}
            </div>
          </div>
        )}
      </div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">
            {data ? `${data.count} project${data.count !== 1 ? 's' : ''}` : ''}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/projects/kanban"
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Kanban View
          </Link>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
          >
            + New Project
          </button>
        </div>
      </div>

      {/* Filters */}
      <div id="projects-filters" className="mb-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search projects…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
        <select
          title="Status filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | '')}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <select
          title="Health filter"
          value={healthFilter}
          onChange={(e) => setHealthFilter(e.target.value as HealthStatus | '')}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        >
          <option value="">All Health</option>
          <option value="green">Healthy</option>
          <option value="yellow">At Risk</option>
          <option value="red">Critical</option>
        </select>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load projects. Please try again.
        </div>
      )}

      {/* Empty */}
      {!isLoading && !error && data?.results.length === 0 && (
        <div className="flex h-40 flex-col items-center justify-center text-slate-400">
          <svg className="mb-3 h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p className="text-sm font-medium">No projects found</p>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="mt-3 text-sm text-amber-600 hover:underline"
          >
            Create your first project
          </button>
        </div>
      )}

      {/* Project grid */}
      {data && data.results.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {data.results.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md block"
            >
              {/* Top row */}
              <div className="mb-3 flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-slate-400">{project.project_number}</p>
                  <h3 className="mt-0.5 truncate text-base font-semibold text-slate-900">
                    {project.name}
                  </h3>
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  {project.health_status && (
                    <span
                      className={`inline-block h-3 w-3 rounded-full ${HEALTH_COLORS[project.health_status]}`}
                      title={project.health_status}
                    />
                  )}
                  <button
                    type="button"
                    onClick={(e) => { e.preventDefault(); setEditProject(project); }}
                    title="Edit project"
                    className="rounded p-1 text-slate-300 opacity-0 transition-opacity hover:bg-slate-100 hover:text-slate-700 group-hover:opacity-100"
                  >
                    <PencilIcon />
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.preventDefault(); setDeleteTarget(project); }}
                    title="Delete project"
                    className="rounded p-1 text-slate-300 opacity-0 transition-opacity hover:bg-red-50 hover:text-red-600 group-hover:opacity-100"
                  >
                    <TrashIcon />
                  </button>
                </div>
              </div>

              {/* Status badge */}
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[project.status]}`}>
                {STATUS_LABELS[project.status]}
              </span>

              {/* Client & PM */}
              {(project.client_name || project.project_manager_name) && (
                <div className="mt-3 space-y-1">
                  {project.client_name && (
                    <p className="truncate text-xs text-slate-500">
                      <span className="font-medium">Client:</span> {project.client_name}
                    </p>
                  )}
                  {project.project_manager_name && (
                    <p className="truncate text-xs text-slate-500">
                      <span className="font-medium">PM:</span> {project.project_manager_name}
                    </p>
                  )}
                  {project.team_name && (
                    <p className="truncate text-xs text-slate-500">
                      <span className="font-medium">Team:</span> {project.team_name}
                    </p>
                  )}
                </div>
              )}

              {/* Value & dates */}
              <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                {project.estimated_value ? (
                  <span>${Number(project.estimated_value).toLocaleString()}</span>
                ) : (
                  <span />
                )}
                {project.estimated_completion && (
                  <span>Due {fmtDate(project.estimated_completion)}</span>
                )}
              </div>

              {/* Health score bar */}
              {project.health_score !== null && (
                <div className="mt-3">
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full transition-all ${
                        project.health_score >= 70
                          ? 'bg-green-500'
                          : project.health_score >= 40
                          ? 'bg-yellow-400'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${project.health_score}%` }}
                    />
                  </div>
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      {/* Modals */}
      {(showCreate || editProject) && (
        <ProjectModal
          project={editProject}
          onClose={() => { setShowCreate(false); setEditProject(null); }}
        />
      )}

      {deleteTarget && (
        <ConfirmDeleteModal
          title="Delete Project"
          description={`Delete "${deleteTarget.name}"? This cannot be undone.`}
          isPending={deleteProject.isPending}
          onConfirm={() => deleteProject.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) })}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
};

// ── Project Modal ─────────────────────────────────────────────────────────────

interface ProjectModalProps {
  project: Project | null;
  onClose: () => void;
}

function ProjectModal({ project, onClose }: ProjectModalProps) {
  const isEdit = !!project;
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();
  const isPending = createProject.isPending || updateProject.isPending;
  const { data: contactsData, isLoading: contactsLoading } = useContacts();

  const { data: teamsData } = useQuery({ queryKey: ['teams'], queryFn: fetchTeams });
  const [nameError, setNameError] = useState('');
  const [form, setForm] = useState({
    name: project?.name ?? '',
    project_type: project?.project_type ?? '',
    client: project?.client ?? '',
    team: project?.team ?? '',
    address: project?.address ?? '',
    city: project?.city ?? '',
    state: project?.state ?? '',
    estimated_value: project?.estimated_value ?? '',
    start_date: project?.start_date ?? '',
    estimated_completion: project?.estimated_completion ?? '',
    description: project?.description ?? '',
  });

  const set = (field: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const [clientError, setClientError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let valid = true;
    if (!form.name.trim()) { setNameError('Project name is required.'); valid = false; }
    else setNameError('');
    if (!form.client) { setClientError('Customer contact is required.'); valid = false; }
    else setClientError('');
    if (!valid) return;

    const payload: Record<string, unknown> = {
      name: form.name.trim(),
      description: form.description,
      project_type: form.project_type,
      address: form.address,
      city: form.city,
      state: form.state,
      estimated_value: form.estimated_value || null,
      start_date: form.start_date || null,
      estimated_completion: form.estimated_completion || null,
    };
    payload.client = form.client || null;
    payload.team = form.team || null;

    if (isEdit) {
      updateProject.mutate(
        { id: project.id, payload: payload as Partial<Project> },
        { onSuccess: onClose },
      );
    } else {
      createProject.mutate(payload as Partial<Project>, { onSuccess: onClose });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">
            {isEdit ? 'Edit Project' : 'New Project'}
          </h2>
          <button type="button" onClick={onClose} title="Close" className="text-slate-400 hover:text-slate-600">
            <XIcon />
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-6 py-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Project Name *">
              <input
                type="text"
                value={form.name}
                onChange={(e) => { set('name')(e); setNameError(''); }}
                required
                className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 ${nameError ? 'border-red-400 focus:border-red-400 focus:ring-red-400' : 'border-slate-200 focus:border-amber-400 focus:ring-amber-400'}`}
                placeholder="e.g. Johnson Kitchen Remodel"
              />
              {nameError && <p className="mt-1 text-xs text-red-600">{nameError}</p>}
            </Field>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Project Type">
                <select
                  title="Project type"
                  value={form.project_type}
                  onChange={set('project_type')}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                >
                  {PROJECT_TYPE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </Field>
              <Field label="Customer Contact *">
                <select
                  title="Client"
                  value={form.client}
                  onChange={(e) => { set('client')(e); setClientError(''); }}
                  disabled={contactsLoading}
                  className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-1 disabled:opacity-60 ${clientError ? 'border-red-400 focus:border-red-400 focus:ring-red-400' : 'border-slate-200 focus:border-amber-400 focus:ring-amber-400'}`}
                >
                  <option value="">{contactsLoading ? 'Loading contacts…' : '— Select customer —'}</option>
                  {contactsData?.results.map((c) => (
                    <option key={c.id} value={c.id}>{c.full_name}</option>
                  ))}
                </select>
                {clientError && <p className="mt-1 text-xs text-red-500">{clientError}</p>}
              </Field>
            </div>

            <Field label="Assigned Team">
              <select
                title="Assigned team"
                value={form.team}
                onChange={set('team')}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              >
                <option value="">— No team —</option>
                {(teamsData ?? []).map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </Field>

            <Field label="Address">
              <input
                type="text"
                value={form.address}
                onChange={set('address')}
                placeholder="Street address"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="City">
                <input
                  type="text"
                  title="City"
                  placeholder="City"
                  value={form.city}
                  onChange={set('city')}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </Field>
              <Field label="State">
                <input
                  type="text"
                  title="State"
                  value={form.state}
                  onChange={set('state')}
                  placeholder="e.g. TX"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </Field>
            </div>

            <Field label="Estimated Value ($)">
              <input
                type="number"
                min="0"
                step="100"
                value={form.estimated_value}
                onChange={set('estimated_value')}
                placeholder="0"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            </Field>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Start Date">
                <input
                  type="date"
                  title="Start date"
                  value={form.start_date}
                  onChange={set('start_date')}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </Field>
              <Field label="Target Completion">
                <input
                  type="date"
                  title="Target completion date"
                  value={form.estimated_completion}
                  onChange={set('estimated_completion')}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </Field>
            </div>

            <Field label="Description">
              <textarea
                title="Description"
                value={form.description}
                onChange={set('description')}
                rows={3}
                placeholder="Project scope and details…"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            </Field>

            <div className="flex justify-end gap-3 border-t border-slate-200 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isPending}
                className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
              >
                {isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Project'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// ── Shared components ─────────────────────────────────────────────────────────

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-700">{label}</label>
      {children}
    </div>
  );
}

function ConfirmDeleteModal({
  title,
  description,
  isPending,
  onConfirm,
  onCancel,
}: {
  title: string;
  description: string;
  isPending: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-xl bg-white shadow-xl p-6">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isPending}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            {isPending ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

function PencilIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  );
}
