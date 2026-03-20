import { useEffect, useRef, useCallback } from 'react';

const IDLE_MS = 30 * 60 * 1000;      // 30 minutes
const WARNING_MS = 28 * 60 * 1000;   // warn at 28 minutes (2-minute warning)

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
 */
export function useIdleLogout({ onWarn, onLogout, enabled }: UseIdleLogoutOptions) {
  const warnTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const logoutTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const warned = useRef(false);

  const clearTimers = useCallback(() => {
    if (warnTimer.current) clearTimeout(warnTimer.current);
    if (logoutTimer.current) clearTimeout(logoutTimer.current);
  }, []);

  const resetTimers = useCallback(() => {
    clearTimers();
    warned.current = false;

    warnTimer.current = setTimeout(() => {
      warned.current = true;
      onWarn();
    }, WARNING_MS);

    logoutTimer.current = setTimeout(() => {
      onLogout();
    }, IDLE_MS);
  }, [clearTimers, onWarn, onLogout]);

  useEffect(() => {
    if (!enabled) return;

    resetTimers();

    ACTIVITY_EVENTS.forEach((evt) =>
      window.addEventListener(evt, resetTimers, { passive: true })
    );

    return () => {
      clearTimers();
      ACTIVITY_EVENTS.forEach((evt) =>
        window.removeEventListener(evt, resetTimers)
      );
    };
  }, [enabled, resetTimers, clearTimers]);
}
