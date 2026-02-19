import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '@/hooks/useProjects';
import type { ProjectStatus, HealthStatus, ProjectFilters } from '@/types/projects';
import { STATUS_LABELS, STATUS_COLORS, HEALTH_COLORS } from '@/types/projects';

const STATUS_OPTIONS: { value: ProjectStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'lead', label: 'Lead' },
  { value: 'prospect', label: 'Prospect' },
  { value: 'estimate', label: 'Estimate' },
  { value: 'proposal', label: 'Proposal' },
  { value: 'contract', label: 'Contract' },
  { value: 'production', label: 'Production' },
  { value: 'punch_list', label: 'Punch List' },
  { value: 'closeout', label: 'Closeout' },
  { value: 'completed', label: 'Completed' },
];

export const ProjectsPage = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | ''>('');
  const [healthFilter, setHealthFilter] = useState<HealthStatus | ''>('');

  const filters: ProjectFilters = {};
  if (search) filters.search = search;
  if (statusFilter) filters.status = statusFilter;
  if (healthFilter) filters.health_status = healthFilter;

  const { data, isLoading, error } = useProjects(filters);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">
            {data ? `${data.count} project${data.count !== 1 ? 's' : ''}` : ''}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search projects…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | '')}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <select
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
        </div>
      )}

      {/* Project grid */}
      {data && data.results.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {data.results.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
            >
              {/* Top row */}
              <div className="mb-3 flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-slate-400">{project.project_number}</p>
                  <h3 className="mt-0.5 truncate text-base font-semibold text-slate-900 group-hover:text-amber-700">
                    {project.name}
                  </h3>
                </div>
                {project.health_status && (
                  <span
                    className={`mt-1 inline-block h-3 w-3 flex-shrink-0 rounded-full ${HEALTH_COLORS[project.health_status]}`}
                    title={project.health_status}
                  />
                )}
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
                </div>
              )}

              {/* Value & dates */}
              <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                {project.estimated_value ? (
                  <span>${Number(project.estimated_value).toLocaleString()}</span>
                ) : (
                  <span />
                )}
                {project.target_completion && (
                  <span>Due {new Date(project.target_completion).toLocaleDateString()}</span>
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
    </div>
  );
};
