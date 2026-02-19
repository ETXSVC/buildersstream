/**
 * QuickClockInOut — large touch-friendly clock in/out button.
 * Captures GPS. Works offline — stores entry in IndexedDB and syncs when online.
 */
import { useState } from 'react';
import { offlineDb } from '@/services/offlineDb';
import { geofenceService } from '@/services/geofenceService';
import { apiClient } from '@/api/client';

type ClockState = 'idle' | 'checking' | 'clocked_in' | 'submitting';

type Props = {
  projectId?: string;
  projectName?: string;
};

export const QuickClockInOut = ({ projectId = '', projectName = 'No project selected' }: Props) => {
  const [state, setState] = useState<ClockState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [clockInTime, setClockInTime] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  const handleClockIn = async () => {
    setState('checking');
    setError(null);
    setWarning(null);

    let position = { latitude: 0, longitude: 0, accuracy: 0 };
    let withinGeofence = true;

    try {
      const check = await geofenceService.checkGeofence(projectId);
      position = check.position;
      withinGeofence = check.isWithin;
      if (!withinGeofence) {
        setWarning(
          `You appear to be ${Math.round(check.distanceMeters)}m from the job site (allowed: ${check.radiusMeters}m). Clocking in anyway.`
        );
      }
    } catch {
      setWarning('GPS unavailable. Clocking in without location.');
    }

    const clockIn = new Date().toISOString();
    const id = `clock_${Date.now()}`;

    if (navigator.onLine) {
      try {
        await apiClient.post('/api/v1/field-ops/time-entries/clock-in/', {
          project: projectId,
          latitude: position.latitude || undefined,
          longitude: position.longitude || undefined,
        });
        setClockInTime(clockIn);
        setState('clocked_in');
        return;
      } catch {
        // Fall through to offline path
      }
    }

    // Offline: store locally
    await offlineDb.saveTimeEntryDraft({
      id,
      projectId,
      clockIn,
      latitude: position.latitude || undefined,
      longitude: position.longitude || undefined,
    });
    setClockInTime(clockIn);
    setState('clocked_in');
  };

  const handleClockOut = async () => {
    setState('submitting');
    try {
      if (navigator.onLine) {
        await apiClient.post('/api/v1/field-ops/time-entries/clock-out/', {
          project: projectId,
        });
      }
      setClockInTime(null);
      setState('idle');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Clock out failed');
      setState('clocked_in');
    }
  };

  const isClockedIn = state === 'clocked_in';
  const isLoading = state === 'checking' || state === 'submitting';

  return (
    <div className="flex flex-col items-center gap-4 p-6">
      <p className="text-sm font-medium text-slate-500">{projectName}</p>

      {warning && (
        <p className="rounded-lg bg-amber-50 px-4 py-2 text-center text-sm text-amber-700">
          {warning}
        </p>
      )}
      {error && (
        <p className="rounded-lg bg-red-50 px-4 py-2 text-center text-sm text-red-700">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={isClockedIn ? handleClockOut : handleClockIn}
        disabled={isLoading}
        aria-label={isClockedIn ? 'Clock Out' : 'Clock In'}
        className={[
          'flex h-40 w-40 flex-col items-center justify-center rounded-full text-white shadow-xl transition-all active:scale-95 disabled:opacity-50',
          isClockedIn
            ? 'bg-red-500 hover:bg-red-600'
            : 'bg-green-500 hover:bg-green-600',
        ].join(' ')}
      >
        {isLoading ? (
          <svg className="h-10 w-10 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
        ) : (
          <>
            <svg className="mb-2 h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-xl font-bold">{isClockedIn ? 'Clock Out' : 'Clock In'}</span>
          </>
        )}
      </button>

      {isClockedIn && clockInTime && (
        <p className="text-sm text-slate-500">
          Clocked in at {new Date(clockInTime).toLocaleTimeString()}
        </p>
      )}

      {!navigator.onLine && (
        <p className="text-xs text-amber-600">Offline — will sync when connected</p>
      )}
    </div>
  );
};
