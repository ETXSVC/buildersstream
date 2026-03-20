/**
 * PushNotificationManager — requests push permission and registers subscription.
 * Handles 4 notification types: approval_needed, schedule_change,
 * message_received, payment_received.
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

type PermissionState = 'default' | 'granted' | 'denied' | 'unsupported' | 'registering' | 'error';

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY ?? '';

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

function subscriptionToPayload(sub: PushSubscription) {
  return {
    endpoint: sub.endpoint,
    keys: {
      p256dh: btoa(String.fromCharCode(...new Uint8Array(sub.getKey('p256dh')!))),
      auth: btoa(String.fromCharCode(...new Uint8Array(sub.getKey('auth')!))),
    },
  };
}

async function getOrCreateSubscription(reg: ServiceWorkerRegistration): Promise<PushSubscription> {
  const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
  try {
    return await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey });
  } catch (err) {
    // NotAllowedError = OS/browser blocked push regardless of Notification.permission
    // (e.g. Windows notifications for Edge are off). Don't retry — propagate.
    if (err instanceof DOMException && err.name === 'NotAllowedError') throw err;
    // Other errors (key mismatch) — unsubscribe existing and retry
    console.warn('Push subscribe failed (may be key mismatch), retrying:', err);
    const existing = await reg.pushManager.getSubscription();
    if (existing) await existing.unsubscribe();
    return await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey });
  }
}

export const PushNotificationManager = () => {
  const [permission, setPermission] = useState<PermissionState>('default');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!('Notification' in window) || !('serviceWorker' in navigator) || !('PushManager' in window)) {
      setPermission('unsupported');
      return;
    }

    const current = Notification.permission as PermissionState;
    setPermission(current);

    if (current === 'granted' && VAPID_PUBLIC_KEY) {
      setPermission('registering');
      navigator.serviceWorker.ready
        .then((reg) => getOrCreateSubscription(reg))
        .then((sub) => apiClient.post('/api/v1/integrations/push-subscriptions/', subscriptionToPayload(sub)))
        .then(() => setPermission('granted'))
        .catch((err) => {
          console.warn('Push registration on mount failed:', err);
          const isBlocked = err instanceof DOMException && err.name === 'NotAllowedError';
          setErrorMsg(
            isBlocked
              ? 'Push blocked by OS. On Windows: Settings → System → Notifications → Microsoft Edge → turn on.'
              : 'Could not register. Tap to retry.'
          );
          setPermission('error');
        });
    }
  }, []);

  const unsubscribe = async () => {
    try {
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.getSubscription();
      const endpoint = sub?.endpoint;
      if (sub) await sub.unsubscribe();
      await apiClient.delete('/api/v1/integrations/push-subscriptions/', { data: endpoint ? { endpoint } : undefined });
    } catch (err) {
      console.warn('Push unsubscribe failed:', err);
    }
    setPermission('default');
  };

  const subscribe = async () => {
    if (!VAPID_PUBLIC_KEY) {
      console.warn('VAPID public key not configured');
      return;
    }
    setPermission('registering');
    setErrorMsg('');
    try {
      const result = await Notification.requestPermission();
      if (result !== 'granted') {
        setPermission(result as PermissionState);
        return;
      }

      const reg = await navigator.serviceWorker.ready;
      const sub = await getOrCreateSubscription(reg);
      await apiClient.post('/api/v1/integrations/push-subscriptions/', subscriptionToPayload(sub));
      setPermission('granted');
    } catch (err) {
      console.warn('Push subscription failed:', err);
      const isBlocked = err instanceof DOMException && err.name === 'NotAllowedError';
      setErrorMsg(
        isBlocked
          ? 'Push blocked by OS. On Windows: Settings → System → Notifications → Microsoft Edge → turn on.'
          : err instanceof Error ? err.message : String(err)
      );
      setPermission('error');
    }
  };

  if (permission === 'unsupported') return null;

  if (permission === 'granted') {
    return (
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">
          <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Push notifications enabled
        </div>
        <button
          type="button"
          onClick={unsubscribe}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-700"
        >
          Disable
        </button>
      </div>
    );
  }

  if (permission === 'denied') {
    return (
      <div className="rounded-lg bg-blue-50 px-4 py-2 text-sm text-blue-700">
        Notifications blocked. Enable in browser settings to receive alerts.
      </div>
    );
  }

  if (permission === 'error') {
    return (
      <button
        type="button"
        onClick={subscribe}
        className="flex items-center gap-2 rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 hover:bg-red-100"
      >
        <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M12 3a9 9 0 100 18A9 9 0 0012 3z" />
        </svg>
        {errorMsg || 'Push setup failed — tap to retry'}
      </button>
    );
  }

  const busy = permission === 'registering';

  return (
    <button
      type="button"
      onClick={subscribe}
      disabled={busy}
      className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
    >
      <svg className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      {busy ? 'Enabling…' : 'Enable Push Notifications'}
    </button>
  );
};
