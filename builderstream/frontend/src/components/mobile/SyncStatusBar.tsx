/**
 * SyncStatusBar — shows pending offline items and sync state.
 * Appears as a subtle banner when there is work queued for sync.
 */
import { useSyncStatus } from '@/hooks/useSyncStatus';

export const SyncStatusBar = () => {
  const { syncing, pending, lastSyncAt, errors, triggerSync } = useSyncStatus();

  if (!syncing && pending === 0 && errors.length === 0) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={[
        'flex items-center justify-between gap-2 px-4 py-2 text-sm',
        errors.length > 0
          ? 'bg-red-50 text-red-700'
          : syncing
          ? 'bg-blue-50 text-blue-700'
          : 'bg-amber-50 text-amber-700',
      ].join(' ')}
    >
      <div className="flex items-center gap-2">
        {syncing ? (
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
        ) : (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        )}
        <span>
          {syncing
            ? 'Syncing…'
            : errors.length > 0
            ? `${errors.length} sync error(s)`
            : `${pending} item${pending !== 1 ? 's' : ''} pending sync`}
        </span>
        {lastSyncAt && !syncing && (
          <span className="text-xs opacity-70">
            Last synced {new Date(lastSyncAt).toLocaleTimeString()}
          </span>
        )}
      </div>

      {!syncing && navigator.onLine && (
        <button
          type="button"
          onClick={triggerSync}
          className="rounded-md px-2 py-0.5 text-xs font-medium underline hover:no-underline"
        >
          Sync now
        </button>
      )}
    </div>
  );
};
