import { useState, useEffect } from 'react';
import { syncManager, SyncStatus } from '@/services/syncManager';

export function useSyncStatus(): SyncStatus & { triggerSync: () => void } {
  const [status, setStatus] = useState<SyncStatus>({
    syncing: false,
    pending: 0,
    lastSyncAt: null,
    errors: [],
  });

  useEffect(() => {
    return syncManager.subscribe(setStatus);
  }, []);

  return { ...status, triggerSync: () => syncManager.drain() };
}
