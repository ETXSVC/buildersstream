import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchDunningRules,
  createDunningRule,
  updateDunningRule,
  deleteDunningRule,
  fetchDunningEvents,
  type DunningRule,
} from '@/api/dunning';

const ACTION_LABELS: Record<string, string> = {
  email_reminder: 'Email Reminder',
  suspend_portal: 'Suspend Portal',
  flag_escalation: 'Flag Escalation',
};

const ACTION_COLORS: Record<string, string> = {
  email_reminder: 'bg-blue-100 text-blue-700',
  suspend_portal: 'bg-orange-100 text-orange-700',
  flag_escalation: 'bg-red-100 text-red-700',
};

function RuleFormModal({
  rule,
  onClose,
  onSaved,
}: {
  rule?: DunningRule;
  onClose: () => void;
  onSaved: () => void;
}) {
  const qc = useQueryClient();
  const isEdit = !!rule;
  const [form, setForm] = useState({
    name: rule?.name ?? '',
    days_past_due: rule?.days_past_due ?? 7,
    action_type: rule?.action_type ?? 'email_reminder',
    email_subject: rule?.email_subject ?? 'Invoice {{invoice_number}} is overdue',
    email_body: rule?.email_body ?? 'Dear {{client_name}},\n\nYour invoice {{invoice_number}} for {{balance_due}} is overdue as of {{due_date}}.\n\nPlease contact us if you have any questions.',
    is_active: rule?.is_active ?? true,
  });
  const [error, setError] = useState<string | null>(null);

  const save = useMutation({
    mutationFn: () =>
      isEdit
        ? updateDunningRule(rule!.id, form)
        : createDunningRule(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dunning-rules'] });
      onSaved();
    },
    onError: () => setError('Failed to save rule. Please check the form.'),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">
            {isEdit ? 'Edit Dunning Rule' : 'New Dunning Rule'}
          </h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4 px-6 py-4">
          {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Rule Name</label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Days Past Due</label>
              <input
                type="number"
                min={1}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                value={form.days_past_due}
                onChange={e => setForm(f => ({ ...f, days_past_due: parseInt(e.target.value) || 1 }))}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Action</label>
              <select
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none"
                value={form.action_type}
                onChange={e => setForm(f => ({ ...f, action_type: e.target.value as DunningRule['action_type'] }))}
              >
                <option value="email_reminder">Email Reminder</option>
                <option value="suspend_portal">Suspend Portal Access</option>
                <option value="flag_escalation">Flag for Escalation</option>
              </select>
            </div>
          </div>

          {form.action_type === 'email_reminder' && (
            <>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Email Subject</label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                  value={form.email_subject}
                  onChange={e => setForm(f => ({ ...f, email_subject: e.target.value }))}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Email Body
                  <span className="ml-2 text-xs font-normal text-slate-400">
                    Variables: {'{{invoice_number}}, {{client_name}}, {{balance_due}}, {{due_date}}'}
                  </span>
                </label>
                <textarea
                  rows={5}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                  value={form.email_body}
                  onChange={e => setForm(f => ({ ...f, email_body: e.target.value }))}
                />
              </div>
            </>
          )}

          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
            />
            Active
          </label>
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
            onClick={() => save.mutate()}
            disabled={!form.name.trim() || save.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {save.isPending ? 'Saving…' : 'Save Rule'}
          </button>
        </div>
      </div>
    </div>
  );
}

export function DunningPage() {
  const qc = useQueryClient();
  const [editRule, setEditRule] = useState<DunningRule | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [activeTab, setActiveTab] = useState<'rules' | 'events'>('rules');

  const { data: rulesData, isLoading: rulesLoading } = useQuery({
    queryKey: ['dunning-rules'],
    queryFn: fetchDunningRules,
  });

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['dunning-events'],
    queryFn: () => fetchDunningEvents(),
    enabled: activeTab === 'events',
  });

  const deleteRule = useMutation({
    mutationFn: deleteDunningRule,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['dunning-rules'] }),
  });

  const rules = rulesData?.results ?? [];
  const events = eventsData?.results ?? [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dunning Workflows</h1>
          <p className="mt-1 text-sm text-slate-500">
            Automatically follow up on overdue invoices with configurable rules.
          </p>
        </div>
        {activeTab === 'rules' && (
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + New Rule
          </button>
        )}
      </div>

      {/* Timeline visualization */}
      {rules.length > 0 && activeTab === 'rules' && (
        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Rule Timeline</h2>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 w-px bg-slate-200" style={{ marginLeft: '3.5rem' }} />
            <div className="space-y-4">
              {[...rules].sort((a, b) => a.days_past_due - b.days_past_due).map(rule => (
                <div key={rule.id} className="flex items-start gap-4">
                  <div className="relative z-10 flex h-8 w-14 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">
                    D+{rule.days_past_due}
                  </div>
                  <div className={`flex-1 rounded-lg border px-4 py-2 ${rule.is_active ? 'border-slate-200 bg-slate-50' : 'border-dashed border-slate-300 bg-white opacity-50'}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-900">{rule.name}</span>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ACTION_COLORS[rule.action_type] ?? ''}`}>
                        {ACTION_LABELS[rule.action_type]}
                      </span>
                    </div>
                    {!rule.is_active && <p className="mt-0.5 text-xs text-slate-400">Inactive</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mt-6 border-b border-slate-200">
        <div className="flex gap-4">
          {(['rules', 'events'] as const).map(tab => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium capitalize transition-colors ${activeTab === tab ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500 hover:text-slate-700'}`}
            >
              {tab === 'rules' ? 'Rules' : 'Event Log'}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'rules' && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-white">
          {rulesLoading ? (
            <div className="flex h-32 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
            </div>
          ) : rules.length === 0 ? (
            <div className="py-12 text-center text-slate-400">
              No rules configured. Create your first dunning rule to get started.
            </div>
          ) : (
            <table className="w-full">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Days Past Due</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map(rule => (
                  <tr key={rule.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">{rule.name}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">Day +{rule.days_past_due}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ACTION_COLORS[rule.action_type] ?? ''}`}>
                        {ACTION_LABELS[rule.action_type]}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium ${rule.is_active ? 'text-green-600' : 'text-slate-400'}`}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setEditRule(rule)}
                          className="text-xs text-indigo-600 hover:underline"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            if (confirm(`Delete rule "${rule.name}"?`)) {
                              deleteRule.mutate(rule.id);
                            }
                          }}
                          className="text-xs text-red-500 hover:underline"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'events' && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-white">
          {eventsLoading ? (
            <div className="flex h-32 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
            </div>
          ) : events.length === 0 ? (
            <div className="py-12 text-center text-slate-400">No dunning events logged yet.</div>
          ) : (
            <table className="w-full">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-4 py-3">Invoice</th>
                  <th className="px-4 py-3">Rule</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Triggered</th>
                  <th className="px-4 py-3">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {events.map(event => (
                  <tr key={event.id} className="text-sm">
                    <td className="px-4 py-3 font-mono text-slate-600">{event.invoice_number}</td>
                    <td className="px-4 py-3 text-slate-700">{event.rule_name ?? '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ACTION_COLORS[event.action_taken] ?? 'bg-slate-100 text-slate-700'}`}>
                        {ACTION_LABELS[event.action_taken] ?? event.action_taken}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">{new Date(event.triggered_at).toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium ${event.success ? 'text-green-600' : 'text-red-600'}`}>
                        {event.success ? 'Success' : 'Failed'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {(showCreate || editRule) && (
        <RuleFormModal
          rule={editRule ?? undefined}
          onClose={() => { setShowCreate(false); setEditRule(null); }}
          onSaved={() => { setShowCreate(false); setEditRule(null); }}
        />
      )}
    </div>
  );
}
