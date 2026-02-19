import { useState } from 'react';
import {
  useContacts,
  useLeads,
  usePipelineStages,
  useCreateContact,
  useUpdateContact,
  useDeleteContact,
  useCreateLead,
  useUpdateLead,
  useDeleteLead,
} from '@/hooks/useCRM';
import type { Contact, Lead, PipelineStage } from '@/types/crm';
import {
  URGENCY_COLORS,
  URGENCY_LABELS,
  PROJECT_TYPE_LABELS,
} from '@/types/crm';

type View = 'leads' | 'contacts';

// ── CRMPage ───────────────────────────────────────────────────────────────────

export const CRMPage = () => {
  const [view, setView] = useState<View>('leads');
  const [search, setSearch] = useState('');

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">CRM</h1>
      </div>

      <div className="mb-6 flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {(['leads', 'contacts'] as View[]).map((v) => (
          <button
            key={v}
            type="button"
            onClick={() => setView(v)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition-colors',
              view === v ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {v}
          </button>
        ))}
      </div>

      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${view}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm w-full max-w-xs text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {view === 'leads' ? (
        <LeadsView search={search} />
      ) : (
        <ContactsView search={search} />
      )}
    </div>
  );
};

// ── Leads View ────────────────────────────────────────────────────────────────

function LeadsView({ search }: { search: string }) {
  const [editLead, setEditLead] = useState<Lead | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Lead | null>(null);

  const params: Record<string, string> = {};
  if (search) params.search = search;
  const { data, isLoading } = useLeads(params);
  const { data: stages } = usePipelineStages();
  const updateLead = useUpdateLead();
  const deleteLead = useDeleteLead();

  if (isLoading) return <Spinner />;

  return (
    <>
      <div className="mb-3 flex justify-end">
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
        >
          + New Lead
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <Th>Contact</Th>
              <Th>Stage</Th>
              <Th>Project Type</Th>
              <Th>Value</Th>
              <Th>Urgency</Th>
              <Th>Follow-up</Th>
              <Th></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                  No leads found. Add your first lead to get started.
                </td>
              </tr>
            )}
            {data?.results.map((lead) => (
              <tr key={lead.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">
                  {lead.contact_name ?? <span className="text-slate-400 italic">No contact</span>}
                </td>
                <td className="px-4 py-3">
                  <select
                    value={lead.pipeline_stage ?? ''}
                    onChange={(e) =>
                      updateLead.mutate({ id: lead.id, payload: { pipeline_stage: e.target.value || null } as Partial<Lead> })
                    }
                    className="rounded border border-slate-200 bg-white px-2 py-1 text-xs text-slate-700 focus:border-amber-400 focus:outline-none"
                  >
                    <option value="">— No stage —</option>
                    {stages?.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {lead.project_type ? PROJECT_TYPE_LABELS[lead.project_type] : '—'}
                </td>
                <td className="px-4 py-3 text-slate-900">
                  {lead.estimated_value ? `$${Number(lead.estimated_value).toLocaleString()}` : '—'}
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${URGENCY_COLORS[lead.urgency]}`}>
                    {URGENCY_LABELS[lead.urgency]}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600 text-xs">
                  {lead.next_follow_up ? new Date(lead.next_follow_up).toLocaleDateString() : '—'}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setEditLead(lead)}
                      className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                      title="Edit"
                    >
                      <PencilIcon />
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(lead)}
                      className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600"
                      title="Delete"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && data.count > data.results.length && (
          <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
            Showing {data.results.length} of {data.count} leads
          </div>
        )}
      </div>

      {(showCreate || editLead) && (
        <LeadModal
          lead={editLead}
          stages={stages ?? []}
          onClose={() => { setShowCreate(false); setEditLead(null); }}
        />
      )}

      {deleteTarget && (
        <ConfirmDeleteModal
          title="Delete Lead"
          description={`Delete the lead for ${deleteTarget.contact_name ?? 'this contact'}? This cannot be undone.`}
          isPending={deleteLead.isPending}
          onConfirm={() => deleteLead.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) })}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </>
  );
}

// ── Contacts View ─────────────────────────────────────────────────────────────

function ContactsView({ search }: { search: string }) {
  const [editContact, setEditContact] = useState<Contact | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Contact | null>(null);

  const { data, isLoading } = useContacts(search || undefined);
  const deleteContact = useDeleteContact();

  if (isLoading) return <Spinner />;

  return (
    <>
      <div className="mb-3 flex justify-end">
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
        >
          + New Contact
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Phone</Th>
              <Th>Company</Th>
              <Th>Title</Th>
              <Th>Score</Th>
              <Th></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.results.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                  No contacts found. Add your first contact to get started.
                </td>
              </tr>
            )}
            {data?.results.map((contact) => (
              <tr key={contact.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-semibold text-amber-700">
                      {contact.first_name[0]}{contact.last_name[0]}
                    </div>
                    <span className="font-medium text-slate-900">{contact.full_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-slate-600">{contact.email ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{contact.phone ?? contact.mobile_phone ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{contact.company_name ?? '—'}</td>
                <td className="px-4 py-3 text-slate-600">{contact.job_title ?? '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={`h-full rounded-full ${contact.lead_score >= 70 ? 'bg-green-500' : contact.lead_score >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                        style={{ width: `${contact.lead_score}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-500">{contact.lead_score}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setEditContact(contact)}
                      className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                      title="Edit"
                    >
                      <PencilIcon />
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(contact)}
                      className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600"
                      title="Delete"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && data.count > data.results.length && (
          <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
            Showing {data.results.length} of {data.count} contacts
          </div>
        )}
      </div>

      {(showCreate || editContact) && (
        <ContactModal
          contact={editContact}
          onClose={() => { setShowCreate(false); setEditContact(null); }}
        />
      )}

      {deleteTarget && (
        <ConfirmDeleteModal
          title="Delete Contact"
          description={`Delete ${deleteTarget.full_name}? This cannot be undone.`}
          isPending={deleteContact.isPending}
          onConfirm={() => deleteContact.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) })}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </>
  );
}

// ── Contact Modal ─────────────────────────────────────────────────────────────

interface ContactModalProps {
  contact: Contact | null;
  onClose: () => void;
}

function ContactModal({ contact, onClose }: ContactModalProps) {
  const isEdit = !!contact;
  const createContact = useCreateContact();
  const updateContact = useUpdateContact();
  const isPending = createContact.isPending || updateContact.isPending;

  const [form, setForm] = useState({
    first_name: contact?.first_name ?? '',
    last_name: contact?.last_name ?? '',
    email: contact?.email ?? '',
    phone: contact?.phone ?? '',
    mobile_phone: contact?.mobile_phone ?? '',
    company_name: contact?.company_name ?? '',
    job_title: contact?.job_title ?? '',
    notes: contact?.notes ?? '',
  });

  const set = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      email: form.email || null,
      phone: form.phone || null,
      mobile_phone: form.mobile_phone || null,
      company_name: form.company_name || null,
      job_title: form.job_title || null,
      notes: form.notes || null,
    };
    if (isEdit) {
      updateContact.mutate({ id: contact.id, payload }, { onSuccess: onClose });
    } else {
      createContact.mutate(payload, { onSuccess: onClose });
    }
  };

  return (
    <Modal title={isEdit ? 'Edit Contact' : 'New Contact'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Field label="First Name *">
            <Input value={form.first_name} onChange={set('first_name')} required />
          </Field>
          <Field label="Last Name *">
            <Input value={form.last_name} onChange={set('last_name')} required />
          </Field>
        </div>
        <Field label="Email">
          <Input type="email" value={form.email} onChange={set('email')} />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Phone">
            <Input value={form.phone} onChange={set('phone')} />
          </Field>
          <Field label="Mobile">
            <Input value={form.mobile_phone} onChange={set('mobile_phone')} />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Company">
            <Input value={form.company_name} onChange={set('company_name')} />
          </Field>
          <Field label="Job Title">
            <Input value={form.job_title} onChange={set('job_title')} />
          </Field>
        </div>
        <Field label="Notes">
          <textarea
            value={form.notes}
            onChange={set('notes')}
            rows={3}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
          />
        </Field>
        <ModalFooter onCancel={onClose} isPending={isPending} submitLabel={isEdit ? 'Save Changes' : 'Create Contact'} />
      </form>
    </Modal>
  );
}

// ── Lead Modal ────────────────────────────────────────────────────────────────

interface LeadModalProps {
  lead: Lead | null;
  stages: PipelineStage[];
  onClose: () => void;
}

function LeadModal({ lead, stages, onClose }: LeadModalProps) {
  const isEdit = !!lead;
  const createLead = useCreateLead();
  const updateLead = useUpdateLead();
  const isPending = createLead.isPending || updateLead.isPending;

  const [form, setForm] = useState({
    pipeline_stage: lead?.pipeline_stage ?? '',
    project_type: lead?.project_type ?? '',
    estimated_value: lead?.estimated_value ?? '',
    estimated_start: lead?.estimated_start ?? '',
    urgency: lead?.urgency ?? 'warm',
    description: lead?.description ?? '',
    next_follow_up: lead?.next_follow_up ?? '',
  });

  const set = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const [stageError, setStageError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // pipeline_stage is required on create (allow_null=False on serializer)
    if (!isEdit && !form.pipeline_stage) {
      setStageError('Please select a pipeline stage.');
      return;
    }
    setStageError('');

    // Build payload carefully matching backend validation:
    // - description/project_type: allow_null=False → send '' not null
    // - estimated_value/start/next_follow_up: allow_null=True → null is OK
    // - pipeline_stage: allow_null=False → only include if non-empty
    const payload: Record<string, unknown> = {
      urgency: form.urgency || 'warm',
      description: form.description,          // '' is valid (allow_blank=True)
      project_type: form.project_type,        // '' is valid (allow_blank=True)
      estimated_value: form.estimated_value || null,
      estimated_start: form.estimated_start || null,
      next_follow_up: form.next_follow_up || null,
    };

    // Only include pipeline_stage when it has a value (required, non-nullable)
    if (form.pipeline_stage) payload.pipeline_stage = form.pipeline_stage;

    if (isEdit) {
      updateLead.mutate({ id: lead.id, payload: payload as Partial<Lead> }, { onSuccess: onClose });
    } else {
      createLead.mutate(payload as Partial<Lead>, { onSuccess: onClose });
    }
  };

  return (
    <Modal title={isEdit ? 'Edit Lead' : 'New Lead'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label={`Pipeline Stage${!isEdit ? ' *' : ''}`}>
          <select
            value={form.pipeline_stage}
            onChange={(e) => { set('pipeline_stage')(e); setStageError(''); }}
            className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-1 ${stageError ? 'border-red-400 focus:border-red-400 focus:ring-red-400' : 'border-slate-200 focus:border-amber-400 focus:ring-amber-400'}`}
          >
            <option value="">— No stage —</option>
            {stages.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          {stageError && <p className="mt-1 text-xs text-red-600">{stageError}</p>}
        </Field>
        <Field label="Project Type">
          <select
            value={form.project_type}
            onChange={set('project_type')}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
          >
            <option value="">— Select type —</option>
            {Object.entries(PROJECT_TYPE_LABELS).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Estimated Value ($)">
            <Input type="number" min="0" step="100" value={form.estimated_value} onChange={set('estimated_value')} placeholder="0" />
          </Field>
          <Field label="Urgency">
            <select
              value={form.urgency}
              onChange={set('urgency')}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
            >
              <option value="hot">Hot – Immediate</option>
              <option value="warm">Warm – 1–3 Months</option>
              <option value="cold">Cold – 3+ Months</option>
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Estimated Start">
            <Input type="date" value={form.estimated_start} onChange={set('estimated_start')} />
          </Field>
          <Field label="Next Follow-up">
            <Input type="date" value={form.next_follow_up} onChange={set('next_follow_up')} />
          </Field>
        </div>
        <Field label="Description">
          <textarea
            value={form.description}
            onChange={set('description')}
            rows={3}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
            placeholder="Project details, scope of work…"
          />
        </Field>
        <ModalFooter onCancel={onClose} isPending={isPending} submitLabel={isEdit ? 'Save Changes' : 'Create Lead'} />
      </form>
    </Modal>
  );
}

// ── Shared UI ─────────────────────────────────────────────────────────────────

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <XIcon />
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
      <label className="mb-1 block text-xs font-medium text-slate-700">{label}</label>
      {children}
    </div>
  );
}

function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
    />
  );
}

function ModalFooter({ onCancel, isPending, submitLabel }: { onCancel: () => void; isPending: boolean; submitLabel: string }) {
  return (
    <div className="flex justify-end gap-3 border-t border-slate-200 pt-4">
      <button
        type="button"
        onClick={onCancel}
        className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={isPending}
        className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
      >
        {isPending ? 'Saving…' : submitLabel}
      </button>
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

function Th({ children }: { children?: React.ReactNode }) {
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
