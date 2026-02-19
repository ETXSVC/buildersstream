/**
 * MobileExpenseCapture — receipt photo + amount entry for field expense capture.
 * Stores with receipt blob in IndexedDB when offline.
 */
import { useRef, useState } from 'react';
import { offlineDb } from '@/services/offlineDb';
import { apiClient } from '@/api/client';

const CATEGORIES = [
  'MATERIALS', 'FUEL', 'EQUIPMENT_RENTAL', 'SUBCONTRACTOR',
  'MEALS', 'TRAVEL', 'PERMITS', 'OTHER',
] as const;

type Props = {
  projectId: string;
  onSaved?: () => void;
};

export const MobileExpenseCapture = ({ projectId, onSaved }: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const [receiptBlob, setReceiptBlob] = useState<Blob | null>(null);
  const [category, setCategory] = useState<string>('OTHER');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [mileage, setMileage] = useState('');
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  const handleReceiptCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setReceiptBlob(file);
    setReceiptPreview(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    if (!amount || parseFloat(amount) <= 0) return;
    setStatus('saving');

    const id = `expense_${Date.now()}_${Math.random().toString(36).slice(2)}`;

    try {
      if (navigator.onLine && !receiptBlob) {
        await apiClient.post('/api/v1/field-ops/expenses/', {
          project: projectId,
          category,
          amount: parseFloat(amount),
          description,
          mileage: mileage ? parseFloat(mileage) : undefined,
        });
      } else {
        // Save to IndexedDB (offline or has receipt blob to upload separately)
        await offlineDb.saveExpenseDraft({
          id,
          projectId,
          category,
          amount: parseFloat(amount),
          description,
          receiptBlob: receiptBlob || undefined,
          mileage: mileage ? parseFloat(mileage) : undefined,
          timestamp: new Date().toISOString(),
        });
      }
      setStatus('saved');
      onSaved?.();
      // Reset form
      setAmount('');
      setDescription('');
      setMileage('');
      setReceiptPreview(null);
      setReceiptBlob(null);
    } catch {
      setStatus('error');
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <h2 className="text-lg font-semibold text-slate-900">Capture Expense</h2>

      {/* Receipt photo */}
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="flex h-32 w-full items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 text-slate-500 hover:border-amber-400 transition-colors"
      >
        {receiptPreview ? (
          <img src={receiptPreview} alt="Receipt" className="h-full w-full rounded-xl object-cover" />
        ) : (
          <div className="flex flex-col items-center gap-1">
            <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-sm">Capture receipt (optional)</span>
          </div>
        )}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleReceiptCapture}
        aria-label="Receipt photo input"
      />

      {/* Category */}
      <div>
        <label htmlFor="expense-category" className="mb-1 block text-sm font-medium text-slate-700">Category</label>
        <select
          id="expense-category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-amber-400 focus:outline-none"
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
          ))}
        </select>
      </div>

      {/* Amount */}
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">Amount ($)</label>
        <input
          type="number"
          inputMode="decimal"
          min="0"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00"
          className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-amber-400 focus:outline-none"
        />
      </div>

      {/* Description */}
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What was this expense for?"
          className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-amber-400 focus:outline-none"
        />
      </div>

      {category === 'FUEL' && (
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Mileage</label>
          <input
            type="number"
            inputMode="decimal"
            value={mileage}
            onChange={(e) => setMileage(e.target.value)}
            placeholder="Miles driven"
            className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-amber-400 focus:outline-none"
          />
        </div>
      )}

      {status === 'error' && (
        <p className="text-sm text-red-600">Failed to save. Check your connection and try again.</p>
      )}
      {status === 'saved' && (
        <p className="text-sm text-green-600">
          {navigator.onLine ? 'Expense saved.' : 'Saved offline — will sync when connected.'}
        </p>
      )}

      <button
        type="button"
        onClick={handleSave}
        disabled={status === 'saving' || !amount || parseFloat(amount) <= 0}
        className="w-full rounded-xl bg-amber-500 py-3 text-base font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
      >
        {status === 'saving' ? 'Saving…' : navigator.onLine ? 'Save Expense' : 'Queue Offline'}
      </button>
    </div>
  );
};
