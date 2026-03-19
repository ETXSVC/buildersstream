import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { KpiCard } from '@/components/KpiCard';
import {
  fetchIssues,
  fetchIssue,
  createIssue,
  transitionIssueStatus,
  addIssueComment,
  fetchIssueTypes,
  fetchSLACompliance,
  type IssueListItem,
  type IssueDetail,
} from '@/api/issues';

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200',
};

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-slate-100 text-slate-700',
  open: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-indigo-100 text-indigo-700',
  pending: 'bg-blue-100 text-blue-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-slate-100 text-slate-500',
};

const STATUS_OPTIONS = ['new', 'open', 'in_progress', 'pending', 'resolved', 'closed'];

function SLABadge({ issue }: { issue: IssueListItem }) {
  if (issue.is_sla_resolution_breached) {
    return <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">SLA Breached</span>;
  }
  if (issue.sla_resolution_due_at && issue.status !== 'resolved' && issue.status !== 'closed') {
    const due = new Date(issue.sla_resolution_due_at);
    const now = new Date();
    const hoursLeft = (due.getTime() - now.getTime()) / 3_600_000;
    if (hoursLeft < 1) {
      return <span className="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700">Due &lt;1h</span>;
    }
  }
  return null;
}

function IssueRow({ issue, onSelect }: { issue: IssueListItem; onSelect: () => void }) {
  return (
    <tr className="cursor-pointer hover:bg-slate-50" onClick={onSelect}>
      <td className="whitespace-nowrap px-4 py-3 text-sm font-mono text-slate-500">{issue.number}</td>
      <td className="max-w-xs px-4 py-3">
        <p className="truncate text-sm font-medium text-slate-900">{issue.title}</p>
        {issue.issue_type_name && (
          <p className="text-xs text-slate-400">{issue.issue_type_name}</p>
        )}
      </td>
      <td className="px-4 py-3">
        <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${PRIORITY_COLORS[issue.priority] ?? ''}`}>
          {issue.priority}
        </span>
      </td>
      <td className="px-4 py-3">
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[issue.status] ?? ''}`}>
          {issue.status.replace('_', ' ')}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-slate-600">{issue.assignee_name ?? '—'}</td>
      <td className="px-4 py-3">
        <SLABadge issue={issue} />
      </td>
      <td className="px-4 py-3 text-xs text-slate-400">
        {new Date(issue.created_at).toLocaleDateString()}
      </td>
    </tr>
  );
}

function IssueDetailPanel({
  issueId,
  onClose,
}: {
  issueId: string;
  onClose: () => void;
}) {
  const qc = useQueryClient();
  const [commentText, setCommentText] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('');

  const { data: issue, isLoading } = useQuery({
    queryKey: ['issues', issueId],
    queryFn: () => fetchIssue(issueId),
  });

  const transition = useMutation({
    mutationFn: (s: string) => transitionIssueStatus(issueId, s),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  const addComment = useMutation({
    mutationFn: (content: string) =>
      addIssueComment(issueId, { content, is_internal: isInternal }),
    onSuccess: () => {
      setCommentText('');
      qc.invalidateQueries({ queryKey: ['issues', issueId] });
    },
  });

  if (isLoading || !issue) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-slate-200 px-6 py-4">
        <div>
          <p className="font-mono text-xs text-slate-400">{issue.number}</p>
          <h2 className="mt-1 text-lg font-semibold text-slate-900">{issue.title}</h2>
        </div>
        <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {/* Status badges */}
        <div className="flex flex-wrap gap-2">
          <span className={`rounded-full border px-2 py-1 text-xs font-medium capitalize ${PRIORITY_COLORS[issue.priority] ?? ''}`}>
            {issue.priority}
          </span>
          <span className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${STATUS_COLORS[issue.status] ?? ''}`}>
            {issue.status.replace('_', ' ')}
          </span>
          {issue.is_sla_resolution_breached && (
            <span className="rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-700">SLA Breached</span>
          )}
        </div>

        {/* Description */}
        {issue.description && (
          <div>
            <h3 className="mb-1 text-sm font-medium text-slate-700">Description</h3>
            <p className="text-sm text-slate-600 whitespace-pre-wrap">{issue.description}</p>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Assignee</span>
            <p className="font-medium text-slate-900">{issue.assignee_name ?? '—'}</p>
          </div>
          <div>
            <span className="text-slate-500">Reporter</span>
            <p className="font-medium text-slate-900">{issue.reporter_name ?? '—'}</p>
          </div>
          <div>
            <span className="text-slate-500">SLA Response Due</span>
            <p className="font-medium text-slate-900">
              {issue.sla_response_due_at ? new Date(issue.sla_response_due_at).toLocaleString() : '—'}
            </p>
          </div>
          <div>
            <span className="text-slate-500">SLA Resolution Due</span>
            <p className="font-medium text-slate-900">
              {issue.sla_resolution_due_at ? new Date(issue.sla_resolution_due_at).toLocaleString() : '—'}
            </p>
          </div>
        </div>

        {/* Transition */}
        <div>
          <h3 className="mb-2 text-sm font-medium text-slate-700">Change Status</h3>
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.filter(s => s !== issue.status).map(s => (
              <button
                key={s}
                type="button"
                onClick={() => transition.mutate(s)}
                disabled={transition.isPending}
                className="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium capitalize text-slate-600 hover:border-indigo-300 hover:text-indigo-700"
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Comments */}
        <div>
          <h3 className="mb-3 text-sm font-medium text-slate-700">
            Comments ({issue.comments.length})
          </h3>
          <div className="space-y-3">
            {issue.comments.map(c => (
              <div key={c.id} className={`rounded-lg p-3 text-sm ${c.is_internal ? 'bg-blue-50 border border-blue-100' : 'bg-slate-50'}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-slate-700">{c.author_name ?? 'Unknown'}</span>
                  <div className="flex items-center gap-2">
                    {c.is_internal && (
                      <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">Internal</span>
                    )}
                    <span className="text-xs text-slate-400">{new Date(c.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <p className="text-slate-600 whitespace-pre-wrap">{c.content}</p>
                {c.replies.map(r => (
                  <div key={r.id} className="ml-4 mt-2 rounded-lg bg-white p-2 text-xs">
                    <span className="font-medium">{r.author_name ?? 'Unknown'}</span>: {r.content}
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Comment form */}
          <div className="mt-4 space-y-2">
            <textarea
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
              rows={3}
              placeholder="Add a comment..."
              value={commentText}
              onChange={e => setCommentText(e.target.value)}
            />
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs text-slate-600">
                <input
                  type="checkbox"
                  checked={isInternal}
                  onChange={e => setIsInternal(e.target.checked)}
                />
                Internal note
              </label>
              <button
                type="button"
                onClick={() => commentText.trim() && addComment.mutate(commentText)}
                disabled={!commentText.trim() || addComment.isPending}
                className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                Add Comment
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CreateIssueModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const qc = useQueryClient();
  const [form, setForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    issue_type: '',
  });
  const [error, setError] = useState<string | null>(null);

  const { data: issueTypes = [] } = useQuery({
    queryKey: ['issue-types'],
    queryFn: fetchIssueTypes,
  });

  const create = useMutation({
    mutationFn: createIssue,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['issues'] });
      onCreated();
    },
    onError: () => setError('Failed to create issue. Please try again.'),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">New Issue</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4 px-6 py-4">
          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Title *</label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
              placeholder="Brief description of the issue"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Priority</label>
              <select
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                value={form.priority}
                onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
              >
                {['critical', 'high', 'medium', 'low'].map(p => (
                  <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Issue Type</label>
              <select
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                value={form.issue_type}
                onChange={e => setForm(f => ({ ...f, issue_type: e.target.value }))}
              >
                <option value="">— Select type —</option>
                {issueTypes.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
            <textarea
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
              rows={4}
              placeholder="Detailed description..."
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() =>
              create.mutate({
                title: form.title,
                description: form.description,
                priority: form.priority,
                issue_type: form.issue_type || undefined,
              })
            }
            disabled={!form.title.trim() || create.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {create.isPending ? 'Creating…' : 'Create Issue'}
          </button>
        </div>
      </div>
    </div>
  );
}

function IssuesDashboard() {
  const { data } = useQuery({ queryKey: ['issues', {}], queryFn: () => fetchIssues({}) });
  const { data: sla } = useQuery({ queryKey: ['issues', 'sla'], queryFn: fetchSLACompliance });

  const stats = useMemo(() => {
    const issues = data?.results ?? [];
    const open = issues.filter(i => !['resolved', 'closed'].includes(i.status)).length;
    const critical = issues.filter(i => i.priority === 'critical').length;
    const breached = issues.filter(i => i.is_sla_resolution_breached).length;
    const resolved = issues.filter(i => ['resolved', 'closed'].includes(i.status)).length;
    const statusCounts = issues.reduce<Record<string, number>>((acc, i) => {
      acc[i.status] = (acc[i.status] ?? 0) + 1;
      return acc;
    }, {});
    const priorityCounts = issues.reduce<Record<string, number>>((acc, i) => {
      acc[i.priority] = (acc[i.priority] ?? 0) + 1;
      return acc;
    }, {});
    return { open, critical, breached, resolved, statusCounts, priorityCounts };
  }, [data]);

  const PRIORITY_C: Record<string, string> = {
    critical: '#dc2626', high: '#f97316', medium: '#f59e0b', low: '#22c55e',
  };
  const STATUS_C: Record<string, string> = {
    new: '#94a3b8', open: '#60a5fa', in_progress: '#818cf8', pending: '#f59e0b',
    resolved: '#22c55e', closed: '#e2e8f0',
  };

  const statusData = Object.entries(stats.statusCounts).map(([k, v]) => ({
    name: k.replace('_', ' '),
    value: v,
    color: STATUS_C[k] ?? '#94a3b8',
  }));
  const priorityData = Object.entries(stats.priorityCounts).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    color: PRIORITY_C[k] ?? '#94a3b8',
  }));
  const slaCompliance = sla ? Math.round((sla.resolution_sla.compliance_pct + sla.response_sla.compliance_pct) / 2) : null;

  return (
    <div className="px-6 pt-4 pb-2">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <KpiCard label="Open Issues" value={stats.open} icon="🐛" accent={stats.open > 0 ? 'blue' : 'default'} />
        <KpiCard label="Critical" value={stats.critical} icon="🚨" accent={stats.critical > 0 ? 'red' : 'default'} />
        <KpiCard label="SLA Compliance" value={slaCompliance !== null ? `${slaCompliance}%` : '—'} icon="⏱️" accent={slaCompliance !== null && slaCompliance < 80 ? 'red' : 'green'} sub={`${stats.breached} breached`} />
        <KpiCard label="Resolved" value={stats.resolved} icon="✅" accent="green" />
      </div>
      {(statusData.length > 0 || priorityData.length > 0) && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 mb-6">
          {statusData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Issues by Status</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={statusData} margin={{ top: 0, right: 8, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {statusData.map(e => <Cell key={e.name} fill={e.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {priorityData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">Issues by Priority</h3>
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

export function IssuesPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (priorityFilter) params.priority = priorityFilter;
  if (search) params.search = search;

  const { data, isLoading } = useQuery({
    queryKey: ['issues', params],
    queryFn: () => fetchIssues(params),
  });

  const { data: sla } = useQuery({
    queryKey: ['issues', 'sla'],
    queryFn: fetchSLACompliance,
  });

  const issues = data?.results ?? [];

  return (
    <div className="flex h-full">
      <div className={`flex flex-col flex-1 overflow-hidden ${selectedId ? 'border-r border-slate-200' : ''}`}>
        {/* Page header */}
        <div className="border-b border-slate-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Issue Tracking</h1>
              {sla && (
                <p className="mt-0.5 text-sm text-slate-500">
                  {sla.total_issues} issues · Response SLA {sla.response_sla.compliance_pct}% · Resolution SLA {sla.resolution_sla.compliance_pct}%
                </p>
              )}
            </div>
            <button
              type="button"
              onClick={() => setShowCreate(true)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              + New Issue
            </button>
          </div>
        </div>
        <IssuesDashboard />
        <div className="border-b border-slate-200 bg-white px-6 py-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <input
              type="text"
              placeholder="Search issues..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus:border-indigo-400 focus:outline-none"
            />
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus:outline-none"
            >
              <option value="">All Statuses</option>
              {STATUS_OPTIONS.map(s => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
            <select
              value={priorityFilter}
              onChange={e => setPriorityFilter(e.target.value)}
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus:outline-none"
            >
              <option value="">All Priorities</option>
              {['critical', 'high', 'medium', 'low'].map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="flex h-64 items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
            </div>
          ) : issues.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center text-slate-400">
              <p className="text-lg font-medium">No issues found</p>
              <p className="text-sm">Create your first issue to get started</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-4 py-3">Number</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Priority</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Assignee</th>
                  <th className="px-4 py-3">SLA</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {issues.map(issue => (
                  <IssueRow
                    key={issue.id}
                    issue={issue}
                    onSelect={() => setSelectedId(issue.id === selectedId ? null : issue.id)}
                  />
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Detail panel */}
      {selectedId && (
        <div className="w-[480px] flex-shrink-0 overflow-hidden bg-white">
          <IssueDetailPanel
            issueId={selectedId}
            onClose={() => setSelectedId(null)}
          />
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <CreateIssueModal
          onClose={() => setShowCreate(false)}
          onCreated={() => setShowCreate(false)}
        />
      )}
    </div>
  );
}
