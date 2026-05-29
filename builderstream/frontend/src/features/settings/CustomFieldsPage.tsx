import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchCustomFieldDefinitions,
  createCustomFieldDefinition,
  updateCustomFieldDefinition,
  deleteCustomFieldDefinition,
  type CustomFieldDefinition,
  type FieldType,
  type ModelName,
} from '@/api/customFields';

// ── Constants ─────────────────────────────────────────────────────────────────

const MODEL_LABELS: Record<ModelName, string> = {
  project: 'Project',
  lead: 'Lead',
  contact: 'Contact',
  company: 'Company',
  invoice: 'Invoice',
  estimate: 'Estimate',
  proposal: 'Proposal',
  service_ticket: 'Service Ticket',
  inspection: 'Inspection',
  daily_log: 'Daily Log',
};

const FIELD_TYPE_LABELS: Record<FieldType, string> = {
  text: 'Text',
  textarea: 'Text Area',
  number: 'Number',
  date: 'Date',
  boolean: 'Yes / No',
  select: 'Single Select',
  multi_select: 'Multi Select',
  url: 'URL',
  email: 'Email',
  phone: 'Phone',
};

const FIELD_TYPE_ICONS: Record<FieldType, string> = {
  text: 'T',
  textarea: '¶',
  number: '#',
  date: '📅',
  boolean: '✓',
  select: '▾',
  multi_select: '☑',
  url: '🔗',
  email: '@',
  phone: '☎',
};

// ── Field Form Modal ──────────────────────────────────────────────────────────

type FormState = {
  model_name: ModelName;
  name: string;
  label: string;
  field_type: FieldType;
  options: string;
  required: boolean;
  placeholder: string;
  help_text_field: string;
  sort_order: number;
  is_active: boolean;
};

function FieldFormModal({
  field,
  onClose,
  onSaved,
}: {
  field?: CustomFieldDefinition;
  onClose: () => void;
  onSaved: () => void;
}) {
  const qc = useQueryClient();
  const isEdit = !!field;
  const [form, setForm] = useState<FormState>({
    model_name: field?.model_name ?? 'project',
    name: field?.name ?? '',
    label: field?.label ?? '',
    field_type: field?.field_type ?? 'text',
    options: field?.options?.join('\n') ?? '',
    required: field?.required ?? false,
    placeholder: field?.placeholder ?? '',
    help_text_field: field?.help_text_field ?? '',
    sort_order: field?.sort_order ?? 0,
    is_active: field?.is_active ?? true,
  });
  const [error, setError] = useState<string | null>(null);

  const needsOptions = form.field_type === 'select' || form.field_type === 'multi_select';

  const save = useMutation({
    mutationFn: () => {
      const payload = {
        model_name: form.model_name,
        name: form.name,
        label: form.label,
        field_type: form.field_type,
        options: needsOptions
          ? form.options.split('\n').map(s => s.trim()).filter(Boolean)
          : [],
        required: form.required,
        placeholder: form.placeholder,
        help_text_field: form.help_text_field,
        sort_order: form.sort_order,
        is_active: form.is_active,
      };
      return isEdit
        ? updateCustomFieldDefinition(field!.id, payload)
        : createCustomFieldDefinition(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['custom-field-definitions'] });
      onSaved();
    },
    onError: (err: unknown) => {
      const msg =
        (err as { response?: { data?: { detail?: string; name?: string[] } } })
          ?.response?.data?.detail ||
        (err as { response?: { data?: { name?: string[] } } })
          ?.response?.data?.name?.[0] ||
        'Failed to save field.';
      setError(msg);
    },
  });

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm(f => ({ ...f, [key]: value }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">
            {isEdit ? 'Edit Custom Field' : 'New Custom Field'}
          </h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="max-h-[70vh] overflow-y-auto space-y-4 px-6 py-4">
          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Module</label>
              <select
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={form.model_name}
                onChange={e => set('model_name', e.target.value as ModelName)}
                disabled={isEdit}
              >
                {(Object.keys(MODEL_LABELS) as ModelName[]).map(m => (
                  <option key={m} value={m}>{MODEL_LABELS[m]}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Field Type</label>
              <select
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={form.field_type}
                onChange={e => set('field_type', e.target.value as FieldType)}
                disabled={isEdit}
              >
                {(Object.keys(FIELD_TYPE_LABELS) as FieldType[]).map(t => (
                  <option key={t} value={t}>{FIELD_TYPE_LABELS[t]}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Internal Name
                <span className="ml-1 text-xs font-normal text-slate-400">(snake_case)</span>
              </label>
              <input
                type="text"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono focus:border-indigo-400 focus:outline-none"
                placeholder="my_field_name"
                value={form.name}
                onChange={e => set('name', e.target.value)}
                disabled={isEdit}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Display Label</label>
              <input
                type="text"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                placeholder="My Field Label"
                value={form.label}
                onChange={e => set('label', e.target.value)}
              />
            </div>
          </div>

          {needsOptions && (
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Options
                <span className="ml-2 text-xs font-normal text-slate-400">one per line</span>
              </label>
              <textarea
                rows={4}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                placeholder="Option 1&#10;Option 2&#10;Option 3"
                value={form.options}
                onChange={e => set('options', e.target.value)}
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Placeholder</label>
              <input
                type="text"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                value={form.placeholder}
                onChange={e => set('placeholder', e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Sort Order</label>
              <input
                type="number"
                min={0}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
                value={form.sort_order}
                onChange={e => set('sort_order', parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Help Text</label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
              placeholder="Short description shown below the field"
              value={form.help_text_field}
              onChange={e => set('help_text_field', e.target.value)}
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.required}
                onChange={e => set('required', e.target.checked)}
              />
              Required
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={e => set('is_active', e.target.checked)}
              />
              Active
            </label>
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
            onClick={() => save.mutate()}
            disabled={!form.name.trim() || !form.label.trim() || save.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {save.isPending ? 'Saving…' : 'Save Field'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export function CustomFieldsPage() {
  const qc = useQueryClient();
  const [selectedModel, setSelectedModel] = useState<ModelName | ''>('');
  const [editField, setEditField] = useState<CustomFieldDefinition | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['custom-field-definitions', selectedModel],
    queryFn: () =>
      fetchCustomFieldDefinitions(
        selectedModel ? { model_name: selectedModel as ModelName } : undefined,
      ),
  });

  const deleteField = useMutation({
    mutationFn: deleteCustomFieldDefinition,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['custom-field-definitions'] }),
  });

  const fields = data?.results ?? [];

  // Group by model_name for display
  const grouped: Partial<Record<ModelName, CustomFieldDefinition[]>> = {};
  for (const f of fields) {
    if (!grouped[f.model_name]) grouped[f.model_name] = [];
    grouped[f.model_name]!.push(f);
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Custom Fields</h1>
          <p className="mt-1 text-sm text-slate-500">
            Extend any module with additional fields unique to your organization.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          + New Field
        </button>
      </div>

      {/* Filter by module */}
      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setSelectedModel('')}
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            selectedModel === ''
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          All Modules
        </button>
        {(Object.keys(MODEL_LABELS) as ModelName[]).map(m => (
          <button
            key={m}
            type="button"
            onClick={() => setSelectedModel(m)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              selectedModel === m
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {MODEL_LABELS[m]}
          </button>
        ))}
      </div>

      {/* Fields list */}
      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          </div>
        ) : fields.length === 0 ? (
          <div className="rounded-xl border-2 border-dashed border-slate-200 py-16 text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100">
              <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-600">No custom fields yet</p>
            <p className="mt-1 text-xs text-slate-400">
              Create your first field to extend any module.
            </p>
            <button
              type="button"
              onClick={() => setShowCreate(true)}
              className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Create Field
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {(Object.keys(grouped) as ModelName[]).sort().map(modelName => (
              <div key={modelName} className="rounded-xl border border-slate-200 bg-white">
                <div className="border-b border-slate-100 px-5 py-3">
                  <h2 className="text-sm font-semibold text-slate-700">
                    {MODEL_LABELS[modelName]}
                    <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-normal text-slate-500">
                      {grouped[modelName]!.length}
                    </span>
                  </h2>
                </div>
                <table className="w-full">
                  <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-5 py-2">Field</th>
                      <th className="px-5 py-2">Type</th>
                      <th className="px-5 py-2">Options</th>
                      <th className="px-5 py-2">Status</th>
                      <th className="px-5 py-2" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {grouped[modelName]!.map(f => (
                      <tr key={f.id} className="hover:bg-slate-50">
                        <td className="px-5 py-3">
                          <p className="text-sm font-medium text-slate-900">{f.label}</p>
                          <p className="font-mono text-xs text-slate-400">{f.name}</p>
                          {f.required && (
                            <span className="mt-0.5 inline-block text-xs text-red-500">Required</span>
                          )}
                        </td>
                        <td className="px-5 py-3">
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                            <span className="text-sm">{FIELD_TYPE_ICONS[f.field_type]}</span>
                            {FIELD_TYPE_LABELS[f.field_type]}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          {f.options.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                              {f.options.slice(0, 3).map(o => (
                                <span key={o} className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">
                                  {o}
                                </span>
                              ))}
                              {f.options.length > 3 && (
                                <span className="text-xs text-slate-400">+{f.options.length - 3} more</span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </td>
                        <td className="px-5 py-3">
                          <span className={`text-xs font-medium ${f.is_active ? 'text-green-600' : 'text-slate-400'}`}>
                            {f.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => setEditField(f)}
                              className="text-xs text-indigo-600 hover:underline"
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                if (confirm(`Delete "${f.label}"? This will remove all stored values.`)) {
                                  deleteField.mutate(f.id);
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
              </div>
            ))}
          </div>
        )}
      </div>

      {(showCreate || editField) && (
        <FieldFormModal
          field={editField ?? undefined}
          onClose={() => { setShowCreate(false); setEditField(null); }}
          onSaved={() => { setShowCreate(false); setEditField(null); }}
        />
      )}
    </div>
  );
}
