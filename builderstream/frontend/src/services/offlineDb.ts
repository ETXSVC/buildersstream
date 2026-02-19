/**
 * IndexedDB wrapper for offline data persistence.
 * Caches: active projects, daily log drafts, time entry drafts,
 * expense drafts (with receipt blobs), and pending photo uploads.
 */

const DB_NAME = 'builderstream-offline';
const DB_VERSION = 1;

export type DraftTimeEntry = {
  id: string;
  projectId: string;
  clockIn: string;
  notes?: string;
  latitude?: number;
  longitude?: number;
};

export type DraftExpense = {
  id: string;
  projectId: string;
  costCode?: string;
  category: string;
  amount: number;
  description: string;
  receiptBlob?: Blob;
  mileage?: number;
  timestamp: string;
};

export type DraftDailyLog = {
  id: string;
  projectId: string;
  logDate: string;
  notes: string;
  weatherConditions?: object;
  pendingPhotoIds?: string[];
  updatedAt: string;
};

export type PendingPhoto = {
  id: string;
  projectId: string;
  albumId?: string;
  blob: Blob;
  description?: string;
  queuedAt: string;
};

export type CachedProject = {
  id: string;
  name: string;
  projectNumber: string;
  status: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  geofenceRadius?: number;
};

const STORES = {
  PROJECTS: 'projects',
  TIME_ENTRIES: 'time_entry_drafts',
  EXPENSES: 'expense_drafts',
  DAILY_LOGS: 'daily_log_drafts',
  PHOTOS: 'pending_photos',
} as const;

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORES.PROJECTS)) {
        db.createObjectStore(STORES.PROJECTS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.TIME_ENTRIES)) {
        db.createObjectStore(STORES.TIME_ENTRIES, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.EXPENSES)) {
        db.createObjectStore(STORES.EXPENSES, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.DAILY_LOGS)) {
        db.createObjectStore(STORES.DAILY_LOGS, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORES.PHOTOS)) {
        db.createObjectStore(STORES.PHOTOS, { keyPath: 'id' });
      }
    };
    req.onsuccess = (e) => resolve((e.target as IDBOpenDBRequest).result);
    req.onerror = () => reject(req.error);
  });
}

function txPut<T>(db: IDBDatabase, store: string, value: T): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, 'readwrite');
    tx.objectStore(store).put(value);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

function txGet<T>(db: IDBDatabase, store: string, key: string): Promise<T | undefined> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, 'readonly');
    const req = tx.objectStore(store).get(key);
    req.onsuccess = () => resolve(req.result as T | undefined);
    req.onerror = () => reject(req.error);
  });
}

function txGetAll<T>(db: IDBDatabase, store: string): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, 'readonly');
    const req = tx.objectStore(store).getAll();
    req.onsuccess = () => resolve(req.result as T[]);
    req.onerror = () => reject(req.error);
  });
}

function txDelete(db: IDBDatabase, store: string, key: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, 'readwrite');
    tx.objectStore(store).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

// ─── Public API ───────────────────────────────────────────────────────────────

export const offlineDb = {
  // Projects
  async cacheProjects(projects: CachedProject[]): Promise<void> {
    const db = await openDb();
    for (const p of projects) await txPut(db, STORES.PROJECTS, p);
  },
  async getProjects(): Promise<CachedProject[]> {
    const db = await openDb();
    return txGetAll<CachedProject>(db, STORES.PROJECTS);
  },
  async getProject(id: string): Promise<CachedProject | undefined> {
    const db = await openDb();
    return txGet<CachedProject>(db, STORES.PROJECTS, id);
  },

  // Time entry drafts
  async saveTimeEntryDraft(entry: DraftTimeEntry): Promise<void> {
    const db = await openDb();
    return txPut(db, STORES.TIME_ENTRIES, entry);
  },
  async getTimeEntryDraft(id: string): Promise<DraftTimeEntry | undefined> {
    const db = await openDb();
    return txGet<DraftTimeEntry>(db, STORES.TIME_ENTRIES, id);
  },
  async getAllTimeEntryDrafts(): Promise<DraftTimeEntry[]> {
    const db = await openDb();
    return txGetAll<DraftTimeEntry>(db, STORES.TIME_ENTRIES);
  },
  async deleteTimeEntryDraft(id: string): Promise<void> {
    const db = await openDb();
    return txDelete(db, STORES.TIME_ENTRIES, id);
  },

  // Daily log drafts
  async saveDailyLogDraft(log: DraftDailyLog): Promise<void> {
    const db = await openDb();
    return txPut(db, STORES.DAILY_LOGS, log);
  },
  async getDailyLogDraft(id: string): Promise<DraftDailyLog | undefined> {
    const db = await openDb();
    return txGet<DraftDailyLog>(db, STORES.DAILY_LOGS, id);
  },
  async getDailyLogDraftForDate(projectId: string, logDate: string): Promise<DraftDailyLog | undefined> {
    const db = await openDb();
    const all = await txGetAll<DraftDailyLog>(db, STORES.DAILY_LOGS);
    return all.find((l) => l.projectId === projectId && l.logDate === logDate);
  },

  // Expense drafts
  async saveExpenseDraft(expense: DraftExpense): Promise<void> {
    const db = await openDb();
    return txPut(db, STORES.EXPENSES, expense);
  },
  async getAllExpenseDrafts(): Promise<DraftExpense[]> {
    const db = await openDb();
    return txGetAll<DraftExpense>(db, STORES.EXPENSES);
  },
  async deleteExpenseDraft(id: string): Promise<void> {
    const db = await openDb();
    return txDelete(db, STORES.EXPENSES, id);
  },

  // Pending photos
  async queuePhoto(photo: PendingPhoto): Promise<void> {
    const db = await openDb();
    return txPut(db, STORES.PHOTOS, photo);
  },
  async getPendingPhotos(): Promise<PendingPhoto[]> {
    const db = await openDb();
    return txGetAll<PendingPhoto>(db, STORES.PHOTOS);
  },
  async deletePendingPhoto(id: string): Promise<void> {
    const db = await openDb();
    return txDelete(db, STORES.PHOTOS, id);
  },
};
