import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { CheckSquare, Star, MessageCircle, Calendar, ChevronRight } from 'lucide-react';
import { fetchPortalDashboard } from '@/api/portal';

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="w-full bg-slate-100 rounded-full h-2.5 mt-1">
      <div
        className="h-2.5 rounded-full bg-blue-500 transition-all"
        style={{ width: `${Math.min(100, value)}%` }}
      />
    </div>
  );
}

function ActionCard({
  to,
  icon: Icon,
  label,
  count,
  color,
}: {
  to: string;
  icon: React.ElementType;
  label: string;
  count: number;
  color: string;
}) {
  return (
    <Link
      to={to}
      className="bg-white rounded-2xl border border-slate-200 p-5 flex items-center gap-4 hover:shadow-md transition-shadow"
    >
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-700">{label}</p>
        {count > 0 ? (
          <p className="text-xs text-blue-600 font-semibold">{count} action{count > 1 ? 's' : ''} needed</p>
        ) : (
          <p className="text-xs text-slate-400">All up to date</p>
        )}
      </div>
      <ChevronRight size={16} className="text-slate-300" />
    </Link>
  );
}

export function PortalDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal', 'dashboard'],
    queryFn: fetchPortalDashboard,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
        Unable to load your project. Please try refreshing.
      </div>
    );
  }

  const { project, pending_approvals, pending_selections, unread_messages, branding } = data;

  const statusLabel: Record<string, string> = {
    lead: 'Lead', prospect: 'Prospect', estimate: 'Estimate',
    proposal: 'Proposal', contract: 'Contract', production: 'In Progress',
    punch_list: 'Punch List', closeout: 'Closeout', completed: 'Completed', canceled: 'Canceled',
  };

  return (
    <div className="space-y-6">
      {branding?.welcome_message && (
        <div className="rounded-2xl bg-blue-50 border border-blue-200 px-5 py-4 text-sm text-blue-800">
          {branding.welcome_message}
        </div>
      )}

      {/* Project Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Your Project</p>
            <h2 className="text-2xl font-bold text-slate-900 mt-0.5">{project.name}</h2>
            <p className="text-sm text-slate-500 mt-0.5">#{project.project_number}</p>
          </div>
          <span className="rounded-full bg-blue-100 text-blue-700 text-xs font-semibold px-3 py-1">
            {statusLabel[project.status] ?? project.status}
          </span>
        </div>

        {project.address && (
          <p className="text-sm text-slate-500 mt-3">📍 {project.address}</p>
        )}

        <div className="mt-4">
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>Progress</span>
            <span className="font-semibold text-slate-700">{project.percent_complete}%</span>
          </div>
          <ProgressBar value={project.percent_complete} />
        </div>

        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          {project.start_date && (
            <div>
              <p className="text-xs text-slate-400">Start Date</p>
              <p className="font-medium text-slate-700">{new Date(project.start_date).toLocaleDateString()}</p>
            </div>
          )}
          {project.estimated_completion && (
            <div>
              <p className="text-xs text-slate-400">Est. Completion</p>
              <p className="font-medium text-slate-700">{new Date(project.estimated_completion).toLocaleDateString()}</p>
            </div>
          )}
          {project.actual_completion && (
            <div className="col-span-2">
              <p className="text-xs text-slate-400">Completed</p>
              <p className="font-medium text-green-700">{new Date(project.actual_completion).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>

      {/* Action Cards */}
      <div>
        <h3 className="text-sm font-semibold text-slate-600 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <ActionCard to="/portal/approvals" icon={CheckSquare} label="Approvals"
            count={pending_approvals} color="bg-blue-100 text-blue-600" />
          <ActionCard to="/portal/selections" icon={Star} label="Selections"
            count={pending_selections} color="bg-blue-100 text-blue-600" />
          <ActionCard to="/portal/messages" icon={MessageCircle} label="Messages"
            count={unread_messages} color="bg-green-100 text-green-600" />
          <ActionCard to="/portal/schedule" icon={Calendar} label="Schedule"
            count={0} color="bg-purple-100 text-purple-600" />
        </div>
      </div>
    </div>
  );
}
