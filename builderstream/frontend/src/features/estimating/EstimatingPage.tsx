import { useState, useEffect } from 'react';
import {
  useEstimates, useProposals,
  useCreateEstimate, useUpdateEstimate, useDeleteEstimate,
  useApproveEstimate, useCopyEstimate, useGenerateProposal,
  useUpdateProposal, useDeleteProposal, useSendProposal,
} from '@/hooks/useEstimating';
import { useContacts } from '@/hooks/useCRM';
import { useProjects } from '@/hooks/useProjects';
import {
  ESTIMATE_STATUS_COLORS, ESTIMATE_STATUS_LABELS,
  PROPOSAL_STATUS_COLORS,
} from '@/types/estimating';
import type { Estimate, Proposal } from '@/types/estimating';

type Tab = 'estimates' | 'proposals';

export const EstimatingPage = () => {
  const [tab, setTab] = useState<Tab>('estimates');
  const [search, setSearch] = useState('');

  // Estimate modal state
  const [editEstimate, setEditEstimate] = useState<Estimate | null>(null);
  const [showEstimateModal, setShowEstimateModal] = useState(false);

  // Generate proposal modal state
  const [generateFromEstimate, setGenerateFromEstimate] = useState<Estimate | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // Send proposal modal state
  const [sendProposalRecord, setSendProposalRecord] = useState<Proposal | null>(null);
  const [showSendModal, setShowSendModal] = useState(false);

  const openNewEstimate = () => { setEditEstimate(null); setShowEstimateModal(true); };
  const openEditEstimate = (e: Estimate) => { setEditEstimate(e); setShowEstimateModal(true); };
  const openGenerateProposal = (e: Estimate) => { setGenerateFromEstimate(e); setShowGenerateModal(true); };
  const openSendProposal = (p: Proposal) => { setSendProposalRecord(p); setShowSendModal(true); };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Estimating</h1>
        {tab === 'estimates' && (
          <button type="button" onClick={openNewEstimate}
            className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 transition-colors">
            + New Estimate
          </button>
        )}
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['estimates', 'proposals'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              tab === t ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t}
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
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {tab === 'estimates' && (
        <EstimatesTable
          search={search}
          onEdit={openEditEstimate}
          onGenerateProposal={openGenerateProposal}
        />
      )}
      {tab === 'proposals' && (
        <ProposalsTable
          search={search}
          onSend={openSendProposal}
        />
      )}

      {showEstimateModal && (
        <EstimateModal
          record={editEstimate}
          onClose={() => setShowEstimateModal(false)}
        />
      )}
      {showGenerateModal && generateFromEstimate && (
        <GenerateProposalModal
          estimate={generateFromEstimate}
          onClose={() => setShowGenerateModal(false)}
        />
      )}
      {showSendModal && sendProposalRecord && (
        <SendProposalModal
          proposal={sendProposalRecord}
          onClose={() => setShowSendModal(false)}
        />
      )}
    </div>
  );
};

/* ── Estimates Table ── */
function EstimatesTable({
  search,
  onEdit,
  onGenerateProposal,
}: {
  search: string;
  onEdit: (e: Estimate) => void;
  onGenerateProposal: (e: Estimate) => void;
}) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useEstimates(params);
  const del = useDeleteEstimate();
  const approve = useApproveEstimate();
  const copy = useCopyEstimate();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Estimate #</Th>
            <Th>Name</Th>
            <Th>Project / Lead</Th>
            <Th>Sections</Th>
            <Th>Subtotal</Th>
            <Th>Total</Th>
            <Th>Valid Until</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No estimates found.</td></tr>
          )}
          {data?.results.map((est) => (
            <tr key={est.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{est.estimate_number}</td>
              <td className="px-4 py-3 text-slate-900 max-w-[200px]">
                <p className="truncate">{est.name}</p>
              </td>
              <td className="px-4 py-3 text-slate-500 text-xs">
                {est.project_name ?? est.lead_title ?? '—'}
              </td>
              <td className="px-4 py-3 text-center text-slate-600">{est.section_count}</td>
              <td className="px-4 py-3 text-slate-900">${parseFloat(est.subtotal).toLocaleString()}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">${parseFloat(est.total).toLocaleString()}</td>
              <td className="px-4 py-3 text-slate-600">
                {est.valid_until ? new Date(est.valid_until).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ESTIMATE_STATUS_COLORS[est.status]}`}>
                  {ESTIMATE_STATUS_LABELS[est.status]}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity min-w-[180px]">
                  <button type="button" onClick={() => onEdit(est)}
                    className="text-xs text-blue-600 hover:underline">Edit</button>
                  <button type="button" onClick={() => onGenerateProposal(est)}
                    className="text-xs text-purple-600 hover:underline">Proposal</button>
                  {est.status === 'in_review' && (
                    <button type="button" onClick={() => approve.mutate(est.id)}
                      className="text-xs text-green-600 hover:underline">Approve</button>
                  )}
                  <button type="button" onClick={() => copy.mutate(est.id)}
                    className="text-xs text-slate-500 hover:underline">Copy</button>
                  <button type="button" onClick={() => { if (confirm('Delete this estimate?')) del.mutate(est.id); }}
                    className="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="estimates" />
    </div>
  );
}

/* ── Proposals Table ── */
function ProposalsTable({
  search,
  onSend,
}: {
  search: string;
  onSend: (p: Proposal) => void;
}) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useProposals(params);
  const del = useDeleteProposal();
  const update = useUpdateProposal();

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Proposal #</Th>
            <Th>Estimate</Th>
            <Th>Client</Th>
            <Th>Total</Th>
            <Th>Sent To</Th>
            <Th>Views</Th>
            <Th>Signed</Th>
            <Th>Status</Th>
            <Th></Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No proposals found.</td></tr>
          )}
          {data?.results.map((prop) => (
            <tr key={prop.id} className="group hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{prop.proposal_number}</td>
              <td className="px-4 py-3 text-slate-600 text-xs">{prop.estimate_number}</td>
              <td className="px-4 py-3 text-slate-900">{prop.client_name}</td>
              <td className="px-4 py-3 font-semibold text-slate-900">${parseFloat(prop.total).toLocaleString()}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{prop.sent_to_email ?? '—'}</td>
              <td className="px-4 py-3 text-center">
                {prop.view_count > 0 ? (
                  <span className="inline-flex items-center gap-1 text-purple-600 text-xs font-medium">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {prop.view_count}
                  </span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-center">
                {prop.is_signed ? (
                  <span className="text-green-600 text-xs font-medium">
                    ✓ {prop.signed_by_name ?? 'Signed'}
                  </span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PROPOSAL_STATUS_COLORS[prop.status]}`}>
                  {prop.status}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {!prop.is_signed && (
                    <button type="button" onClick={() => onSend(prop)}
                      className="text-xs text-blue-600 hover:underline">Send</button>
                  )}
                  {prop.status === 'draft' && (
                    <button type="button"
                      onClick={() => update.mutate({ id: prop.id, payload: { status: 'sent' } })}
                      className="text-xs text-slate-500 hover:underline">Mark Sent</button>
                  )}
                  <button type="button" onClick={() => { if (confirm('Delete this proposal?')) del.mutate(prop.id); }}
                    className="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="proposals" />
    </div>
  );
}

/* ── Estimate Modal ── */
function EstimateModal({ record, onClose }: { record: Estimate | null; onClose: () => void }) {
  const isEdit = !!record;
  const { data: projectsData } = useProjects();
  const create = useCreateEstimate();
  const update = useUpdateEstimate();

  const [form, setForm] = useState({
    name: '', status: 'draft', project: '',
    tax_rate: '0', valid_until: '', notes: '',
  });

  useEffect(() => {
    setForm({
      name: record?.name ?? '',
      status: record?.status ?? 'draft',
      project: record?.project ?? '',
      tax_rate: record?.tax_rate ?? '0',
      valid_until: record?.valid_until ?? '',
      notes: '',
    });
  }, [record]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {
      name: form.name,
      status: form.status,
      tax_rate: form.tax_rate || '0',
    };
    if (form.project) payload.project = form.project;
    if (form.valid_until) payload.valid_until = form.valid_until;
    if (form.notes) payload.notes = form.notes;

    if (isEdit) {
      update.mutate({ id: record!.id, payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal title={isEdit ? 'Edit Estimate' : 'New Estimate'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Estimate Name *">
          <input
            required
            title="Estimate name"
            value={form.name}
            onChange={(e) => set('name', e.target.value)}
            placeholder="e.g. Kitchen Remodel — Phase 1"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
        </Field>
        <Field label="Status">
          <select
            title="Status"
            value={form.status}
            onChange={(e) => set('status', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            <option value="draft">Draft</option>
            <option value="in_review">In Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="sent_to_client">Sent to Client</option>
          </select>
        </Field>
        <Field label="Project">
          <select
            title="Project"
            value={form.project}
            onChange={(e) => set('project', e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            <option value="">— No project —</option>
            {projectsData?.results.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Tax Rate (%)">
            <input
              title="Tax rate"
              type="number"
              step="0.01"
              min="0"
              max="100"
              value={form.tax_rate}
              onChange={(e) => set('tax_rate', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </Field>
          <Field label="Valid Until">
            <input
              title="Valid until"
              type="date"
              value={form.valid_until}
              onChange={(e) => set('valid_until', e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </Field>
        </div>
        {!isEdit && (
          <Field label="Notes">
            <textarea
              title="Notes"
              rows={3}
              value={form.notes}
              onChange={(e) => set('notes', e.target.value)}
              placeholder="Internal notes…"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </Field>
        )}
        <ModalActions onClose={onClose} busy={busy} isEdit={isEdit} />
      </form>
    </Modal>
  );
}

/* ── Generate Proposal Modal ── */
function GenerateProposalModal({ estimate, onClose }: { estimate: Estimate; onClose: () => void }) {
  const { data: contactsData } = useContacts();
  const generate = useGenerateProposal();

  const [clientId, setClientId] = useState('');
  const [validUntil, setValidUntil] = useState('');
  const [clientError, setClientError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId) {
      setClientError('Please select a client.');
      return;
    }
    setClientError('');
    const payload: Record<string, unknown> = { client_id: clientId };
    if (validUntil) payload.valid_until = validUntil;

    generate.mutate(
      { estimateId: estimate.id, payload },
      { onSuccess: onClose },
    );
  };

  return (
    <Modal title={`Generate Proposal — ${estimate.estimate_number}`} onClose={onClose}>
      <p className="mb-4 text-sm text-slate-500">
        This will create a client-facing proposal from estimate <strong>{estimate.name}</strong> (${parseFloat(estimate.total).toLocaleString()}).
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Client *">
          <select
            title="Client"
            value={clientId}
            onChange={(e) => { setClientId(e.target.value); setClientError(''); }}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            <option value="">— Select a contact —</option>
            {contactsData?.results.map((c) => (
              <option key={c.id} value={c.id}>
                {c.first_name} {c.last_name}{c.company_name ? ` — ${c.company_name}` : ''}
              </option>
            ))}
          </select>
          {clientError && <p className="mt-1 text-xs text-red-500">{clientError}</p>}
        </Field>
        <Field label="Valid Until">
          <input
            title="Valid until"
            type="date"
            value={validUntil}
            onChange={(e) => setValidUntil(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
        </Field>
        {generate.isError && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {(generate.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Failed to generate proposal. Please try again.'}
          </p>
        )}
        <ModalActions onClose={onClose} busy={generate.isPending} isEdit={false} submitLabel="Generate" />
      </form>
    </Modal>
  );
}

/* ── Send Proposal Modal ── */
function SendProposalModal({ proposal, onClose }: { proposal: Proposal; onClose: () => void }) {
  const send = useSendProposal();
  const [email, setEmail] = useState(proposal.sent_to_email ?? '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send.mutate({ id: proposal.id, email: email || undefined }, { onSuccess: onClose });
  };

  return (
    <Modal title={`Send Proposal — ${proposal.proposal_number}`} onClose={onClose}>
      <p className="mb-4 text-sm text-slate-500">
        Sending to <strong>{proposal.client_name}</strong>. A link to view and sign the proposal will be emailed.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Recipient Email">
          <input
            title="Recipient email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={`${proposal.client_name.toLowerCase().replace(/\s+/, '.')}@example.com`}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
        </Field>
        <ModalActions onClose={onClose} busy={send.isPending} isEdit={false} submitLabel="Send Proposal" />
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
          <button type="button" title="Close" onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
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

function ModalActions({
  onClose,
  busy,
  isEdit,
  submitLabel,
}: {
  onClose: () => void;
  busy: boolean;
  isEdit: boolean;
  submitLabel?: string;
}) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onClose}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
        Cancel
      </button>
      <button type="submit" disabled={busy}
        className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-60">
        {busy ? 'Saving…' : submitLabel ?? (isEdit ? 'Save Changes' : 'Create')}
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
      <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
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
