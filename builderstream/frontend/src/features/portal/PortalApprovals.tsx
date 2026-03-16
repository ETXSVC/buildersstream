import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchPortalApprovals, respondToApproval, type PortalApproval } from '@/api/portal';

const STATUS_STYLES: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  EXPIRED: 'bg-slate-100 text-slate-500',
};

const TYPE_LABELS: Record<string, string> = {
  change_order: 'Change Order',
  draw_request: 'Draw Request',
  design_modification: 'Design Change',
  material_substitution: 'Material Substitution',
  schedule_change: 'Schedule Change',
  other: 'Other',
};

function ApprovalCard({ approval }: { approval: PortalApproval }) {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState('');
  const [confirming, setConfirming] = useState<'approve' | 'reject' | null>(null);

  const mutation = useMutation({
    mutationFn: ({ approved, notes }: { approved: boolean; notes: string }) =>
      respondToApproval(approval.id, approved, notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portal', 'approvals'] });
      qc.invalidateQueries({ queryKey: ['portal', 'dashboard'] });
      setConfirming(null);
    },
  });

  const isPending = approval.status === 'PENDING';
  const isExpired = approval.status === 'EXPIRED';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div
        className="flex items-center justify-between p-5 cursor-pointer"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[approval.status] ?? 'bg-slate-100 text-slate-600'}`}>
              {approval.status}
            </span>
            <span className="text-xs text-slate-400">
              {TYPE_LABELS[approval.approval_type] ?? approval.approval_type}
            </span>
          </div>
          <h3 className="font-semibold text-slate-900 mt-1">{approval.title}</h3>
          {approval.amount && (
            <p className="text-sm font-medium text-slate-600 mt-0.5">
              ${parseFloat(approval.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </p>
          )}
        </div>
        <div className="ml-3 text-slate-400">
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {expanded && (
        <div className="border-t border-slate-100 px-5 pb-5 pt-4 space-y-4">
          {approval.description && (
            <p className="text-sm text-slate-600 whitespace-pre-wrap">{approval.description}</p>
          )}

          <div className="flex gap-4 text-xs text-slate-500">
            <span>Submitted: {new Date(approval.created_at).toLocaleDateString()}</span>
            {approval.expires_at && !isExpired && (
              <span className="text-amber-600 font-medium flex items-center gap-1">
                <Clock size={12} />
                Expires: {new Date(approval.expires_at).toLocaleDateString()}
              </span>
            )}
          </div>

          {isPending && !confirming && (
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setConfirming('approve')}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-xl text-sm font-medium"
              >
                <CheckCircle size={15} /> Approve
              </button>
              <button
                type="button"
                onClick={() => setConfirming('reject')}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-medium"
              >
                <XCircle size={15} /> Reject
              </button>
            </div>
          )}

          {isPending && confirming && (
            <div className="space-y-3">
              <p className="text-sm font-medium text-slate-700">
                {confirming === 'approve' ? '✅ Confirm Approval' : '❌ Confirm Rejection'}
              </p>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Notes (optional)"
                rows={2}
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none"
              />
              {mutation.isError && (
                <p className="text-xs text-red-500">Something went wrong. Please try again.</p>
              )}
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={mutation.isPending}
                  onClick={() => mutation.mutate({ approved: confirming === 'approve', notes })}
                  className={`px-4 py-2 rounded-xl text-sm font-medium text-white disabled:opacity-50 ${
                    confirming === 'approve' ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'
                  }`}
                >
                  {mutation.isPending ? 'Submitting…' : 'Confirm'}
                </button>
                <button
                  type="button"
                  onClick={() => { setConfirming(null); setNotes(''); }}
                  className="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function PortalApprovals() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal', 'approvals'],
    queryFn: fetchPortalApprovals,
    staleTime: 30_000,
  });

  const pending = data?.filter((a) => a.status === 'PENDING') ?? [];
  const resolved = data?.filter((a) => a.status !== 'PENDING') ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Approvals</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load approvals.
        </div>
      )}

      {data && (
        <>
          {pending.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-amber-600 mb-3">
                ⏳ Needs Your Response ({pending.length})
              </h2>
              <div className="space-y-3">
                {pending.map((a) => <ApprovalCard key={a.id} approval={a} />)}
              </div>
            </section>
          )}

          {resolved.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-slate-500 mb-3">Past Approvals</h2>
              <div className="space-y-3">
                {resolved.map((a) => <ApprovalCard key={a.id} approval={a} />)}
              </div>
            </section>
          )}

          {data.length === 0 && (
            <div className="rounded-2xl bg-white border border-slate-200 p-10 text-center text-slate-400 text-sm">
              No approvals yet.
            </div>
          )}
        </>
      )}
    </div>
  );
}
