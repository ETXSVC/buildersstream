import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, Clock } from 'lucide-react';
import {
  fetchPortalSelections,
  submitSelectionChoice,
  type PortalSelection,
  type PortalSelectionOption,
} from '@/api/portal';

const STATUS_STYLES: Record<string, string> = {
  PENDING: 'bg-slate-100 text-slate-600',
  CLIENT_REVIEW: 'bg-blue-100 text-blue-700',
  APPROVED: 'bg-green-100 text-green-700',
  ORDERED: 'bg-blue-100 text-blue-700',
  INSTALLED: 'bg-teal-100 text-teal-700',
};

function OptionCard({
  option,
  selected,
  onClick,
  disabled,
}: {
  option: PortalSelectionOption;
  selected: boolean;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`text-left w-full rounded-xl border-2 p-4 transition-all ${
        selected
          ? 'border-blue-500 bg-blue-50'
          : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/30'
      } ${disabled && !selected ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {option.image_url && (
        <img
          src={option.image_url}
          alt={option.name}
          className="w-full h-36 object-cover rounded-lg mb-3"
        />
      )}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-slate-900 text-sm">{option.name}</p>
          {option.supplier && <p className="text-xs text-slate-500 mt-0.5">{option.supplier}</p>}
          {option.description && <p className="text-xs text-slate-500 mt-1">{option.description}</p>}
          {option.lead_time_days != null && (
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <Clock size={10} /> {option.lead_time_days}d lead time
            </p>
          )}
        </div>
        {selected && <CheckCircle size={18} className="text-blue-500 shrink-0" />}
      </div>
      {option.price && (
        <p className="text-sm font-semibold text-slate-800 mt-2">
          ${parseFloat(option.price).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          {option.price_difference && parseFloat(option.price_difference) !== 0 && (
            <span className={`text-xs ml-1 ${parseFloat(option.price_difference) > 0 ? 'text-red-500' : 'text-green-600'}`}>
              ({parseFloat(option.price_difference) > 0 ? '+' : ''}${parseFloat(option.price_difference).toFixed(2)})
            </span>
          )}
        </p>
      )}
      {option.is_recommended && (
        <span className="inline-block mt-2 bg-blue-100 text-blue-700 text-xs font-medium px-2 py-0.5 rounded-full">
          ⭐ Recommended
        </span>
      )}
    </button>
  );
}

function SelectionCard({ selection }: { selection: PortalSelection }) {
  const qc = useQueryClient();
  const [chosen, setChosen] = useState<string | null>(selection.selected_option);
  const [notes, setNotes] = useState('');
  const canChoose = selection.status === 'CLIENT_REVIEW';

  const mutation = useMutation({
    mutationFn: () => submitSelectionChoice(selection.id, chosen!, notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portal', 'selections'] });
      qc.invalidateQueries({ queryKey: ['portal', 'dashboard'] });
    },
  });

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h3 className="font-semibold text-slate-900">{selection.name}</h3>
          {selection.category && <p className="text-xs text-slate-500 mt-0.5">{selection.category}</p>}
          {selection.notes && <p className="text-sm text-slate-600 mt-1">{selection.notes}</p>}
        </div>
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[selection.status] ?? 'bg-slate-100 text-slate-600'}`}>
            {selection.status.replace('_', ' ')}
          </span>
          {selection.due_date && (
            <span className="text-xs text-blue-600 flex items-center gap-1">
              <Clock size={11} />
              Due {new Date(selection.due_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {selection.options.map((opt) => (
          <OptionCard
            key={opt.id}
            option={opt}
            selected={chosen === opt.id}
            disabled={!canChoose}
            onClick={() => setChosen(opt.id)}
          />
        ))}
      </div>

      {canChoose && (
        <div className="pt-2 space-y-3">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any notes or questions (optional)"
            rows={2}
            className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
          />
          {mutation.isError && (
            <p className="text-xs text-red-500">Failed to submit. Please try again.</p>
          )}
          {mutation.isSuccess && (
            <p className="text-xs text-green-600">✓ Choice submitted successfully.</p>
          )}
          <button
            type="button"
            disabled={!chosen || mutation.isPending}
            onClick={() => mutation.mutate()}
            className="px-5 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl text-sm font-medium disabled:opacity-50"
          >
            {mutation.isPending ? 'Submitting…' : 'Submit My Choice'}
          </button>
        </div>
      )}

      {!canChoose && selection.selected_option && (
        <p className="text-xs text-green-600 font-medium">
          ✓ Selection submitted
        </p>
      )}
    </div>
  );
}

export function PortalSelections() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal', 'selections'],
    queryFn: fetchPortalSelections,
    staleTime: 30_000,
  });

  const pending = data?.filter((s) => s.status === 'CLIENT_REVIEW') ?? [];
  const other = data?.filter((s) => s.status !== 'CLIENT_REVIEW') ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Selections</h1>
      <p className="text-sm text-slate-500">
        Review your material and finish options below. Choose your preference for each pending selection.
      </p>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load selections.
        </div>
      )}

      {data && (
        <>
          {pending.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-blue-600 mb-3">
                ⏳ Awaiting Your Choice ({pending.length})
              </h2>
              <div className="space-y-4">
                {pending.map((s) => <SelectionCard key={s.id} selection={s} />)}
              </div>
            </section>
          )}

          {other.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-slate-500 mb-3">Other Selections</h2>
              <div className="space-y-4">
                {other.map((s) => <SelectionCard key={s.id} selection={s} />)}
              </div>
            </section>
          )}

          {data.length === 0 && (
            <div className="rounded-2xl bg-white border border-slate-200 p-10 text-center text-slate-400 text-sm">
              No selections yet.
            </div>
          )}
        </>
      )}
    </div>
  );
}
