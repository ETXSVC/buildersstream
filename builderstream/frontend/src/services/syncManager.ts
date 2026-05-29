/**
 * SyncManager — drains offline queues when connectivity is restored.
 * Handles time entry, expense, daily log, and photo upload sync in order.
 * Emits sync status updates via a simple event emitter pattern.
 */

import { offlineDb } from './offlineDb';
import { apiClient } from '@/api/client';

export type SyncStatus = {
  syncing: boolean;
  pending: number;
  lastSyncAt: string | null;
  errors: string[];
};

type SyncListener = (status: SyncStatus) => void;

class SyncManagerService {
  private listeners: SyncListener[] = [];
  private status: SyncStatus = {
    syncing: false,
    pending: 0,
    lastSyncAt: null,
    errors: [],
  };

  constructor() {
    // Listen for online events to trigger drain
    window.addEventListener('online', () => {
      this.drain();
      // Also trigger background sync if SW supports it
      if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready
          .then((reg) => (reg as ServiceWorkerRegistration & { sync: { register: (tag: string) => Promise<void> } }).sync.register('builderstream-sync'))
          .catch(() => undefined);
      }
    });
  }

  subscribe(listener: SyncListener): () => void {
    this.listeners.push(listener);
    listener(this.status);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private emit(update: Partial<SyncStatus>) {
    this.status = { ...this.status, ...update };
    this.listeners.forEach((l) => l(this.status));
  }

  async getPendingCount(): Promise<number> {
    const [timeEntries, expenses, photos] = await Promise.all([
      offlineDb.getAllTimeEntryDrafts(),
      offlineDb.getAllExpenseDrafts(),
      offlineDb.getPendingPhotos(),
    ]);
    return timeEntries.length + expenses.length + photos.length;
  }

  async drain(): Promise<void> {
    if (!navigator.onLine || this.status.syncing) return;

    const pending = await this.getPendingCount();
    if (pending === 0) return;

    this.emit({ syncing: true, pending, errors: [] });

    const errors: string[] = [];

    // 1. Sync time entry drafts
    const timeEntries = await offlineDb.getAllTimeEntryDrafts();
    for (const entry of timeEntries) {
      try {
        await apiClient.post('/api/v1/field-ops/time-entries/', {
          project: entry.projectId,
          clock_in: entry.clockIn,
          notes: entry.notes,
          entry_type: 'MANUAL',
          latitude: entry.latitude,
          longitude: entry.longitude,
        });
        await offlineDb.deleteTimeEntryDraft(entry.id);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Time entry sync failed';
        errors.push(msg);
      }
    }

    // 2. Sync expense drafts
    const expenses = await offlineDb.getAllExpenseDrafts();
    for (const expense of expenses) {
      try {
        const formData = new FormData();
        formData.append('project', expense.projectId);
        formData.append('category', expense.category);
        formData.append('amount', expense.amount.toString());
        formData.append('description', expense.description);
        if (expense.costCode) formData.append('cost_code', expense.costCode);
        if (expense.mileage) formData.append('mileage', expense.mileage.toString());
        if (expense.receiptBlob) {
          formData.append('receipt', expense.receiptBlob, 'receipt.jpg');
        }
        await apiClient.post('/api/v1/field-ops/expenses/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        await offlineDb.deleteExpenseDraft(expense.id);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Expense sync failed';
        errors.push(msg);
      }
    }

    // 3. Sync pending photos
    const photos = await offlineDb.getPendingPhotos();
    for (const photo of photos) {
      try {
        // Get presigned upload URL
        const { data: presignData } = await apiClient.post('/api/v1/documents/photos/upload-url/', {
          project: photo.projectId,
          album: photo.albumId,
          file_name: `photo_${photo.id}.jpg`,
          file_type: 'image/jpeg',
        });
        // PUT to S3
        await fetch(presignData.upload_url, {
          method: 'PUT',
          body: photo.blob,
          headers: { 'Content-Type': 'image/jpeg' },
        });
        // Notify server upload complete
        await apiClient.post('/api/v1/documents/photos/upload-complete/', {
          file_key: presignData.file_key,
          project: photo.projectId,
          album: photo.albumId,
          description: photo.description,
        });
        await offlineDb.deletePendingPhoto(photo.id);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Photo sync failed';
        errors.push(msg);
      }
    }

    const remainingPending = await this.getPendingCount();
    this.emit({
      syncing: false,
      pending: remainingPending,
      lastSyncAt: new Date().toISOString(),
      errors,
    });
  }
}

export const syncManager = new SyncManagerService();
