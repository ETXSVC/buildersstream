/**
 * PushNotificationManager — requests push permission and registers subscription.
 * Handles 4 notification types: approval_needed, schedule_change,
 * message_received, payment_received.
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

type PermissionState = 'default' | 'granted' | 'denied' | 'unsupported';

// VAPID public key — replace with actual key from server in production
const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY ?? '';

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

export const PushNotificationManager = () => {
  const [permission, setPermission] = useState<PermissionState>('default');
  const [subscribing, setSubscribing] = useState(false);

  useEffect(() => {
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      setPermission('unsupported');
      return;
    }
    setPermission(Notification.permission as PermissionState);
  }, []);

  const subscribe = async () => {
    if (!VAPID_PUBLIC_KEY) return;
    setSubscribing(true);
    try {
      const result = await Notification.requestPermission();
      setPermission(result as PermissionState);
      if (result !== 'granted') return;

      const reg = await navigator.serviceWorker.ready;
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      // Register subscription with backend
      await apiClient.post('/api/v1/integrations/push-subscriptions/', {
        endpoint: subscription.endpoint,
        keys: {
          p256dh: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('p256dh')!))),
          auth: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('auth')!))),
        },
      });
    } catch (err) {
      console.warn('Push subscription failed:', err);
    } finally {
      setSubscribing(false);
    }
  };

  if (permission === 'unsupported') return null;

  if (permission === 'granted') {
    return (
      <div className="flex items-center gap-2 rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">
        <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        Push notifications enabled
      </div>
    );
  }

  if (permission === 'denied') {
    return (
      <div className="rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-700">
        Notifications blocked. Enable in browser settings to receive alerts.
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={subscribe}
      disabled={subscribing}
      className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
    >
      <svg className="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      {subscribing ? 'Enabling…' : 'Enable Push Notifications'}
    </button>
  );
};
