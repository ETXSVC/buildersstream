import { useEffect, useRef, useCallback } from 'react';

const IDLE_MS = 30 * 60 * 1000;      // 30 minutes
const WARNING_MS = 28 * 60 * 1000;   // warn at 28 minutes (2-minute warning)
const THROTTLE_MS = 1_000;           // mousemove throttle

const ACTIVITY_EVENTS = [
  'mousemove',
  'mousedown',
  'keydown',
  'touchstart',
  'scroll',
  'click',
];

interface UseIdleLogoutOptions {
  onWarn: () => void;
  onLogout: () => void;
  enabled: boolean;
}

/**
 * Tracks user inactivity. After WARNING_MS of no activity calls `onWarn`.
 * After IDLE_MS calls `onLogout`. Any activity resets both timers.
 * mousemove is throttled to once per THROTTLE_MS to avoid CPU churn.
 */
export function useIdleLogout({ onWarn, onLogout, enabled }: UseIdleLogoutOptions) {
  const warnTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const logoutTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastReset = useRef<number>(0);

  const clearTimers = useCallback(() => {
    if (warnTimer.current) clearTimeout(warnTimer.current);
    if (logoutTimer.current) clearTimeout(logoutTimer.current);
  }, []);

  const resetTimers = useCallback(() => {
    clearTimers();

    warnTimer.current = setTimeout(() => {
      onWarn();
    }, WARNING_MS);

    logoutTimer.current = setTimeout(() => {
      onLogout();
    }, IDLE_MS);
  }, [clearTimers, onWarn, onLogout]);

  const handleActivity = useCallback((evt: Event) => {
    if (evt.type === 'mousemove') {
      const now = Date.now();
      if (now - lastReset.current < THROTTLE_MS) return;
      lastReset.current = now;
    }
    resetTimers();
  }, [resetTimers]);

  useEffect(() => {
    if (!enabled) return;

    resetTimers();

    ACTIVITY_EVENTS.forEach((evt) =>
      window.addEventListener(evt, handleActivity, { passive: true })
    );

    return () => {
      clearTimers();
      ACTIVITY_EVENTS.forEach((evt) =>
        window.removeEventListener(evt, handleActivity)
      );
    };
  }, [enabled, resetTimers, clearTimers, handleActivity]);
}
