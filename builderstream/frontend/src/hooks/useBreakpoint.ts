/**
 * useBreakpoint — detects current viewport breakpoint.
 * Returns 'mobile' | 'tablet' | 'desktop' based on Tailwind screen sizes.
 *   mobile:  < 640px  (sm)
 *   tablet:  640–1023px
 *   desktop: >= 1024px (lg)
 */
import { useState, useEffect } from 'react';

export type Breakpoint = 'mobile' | 'tablet' | 'desktop';

function getBreakpoint(width: number): Breakpoint {
  if (width < 640) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
}

export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>(
    () => getBreakpoint(window.innerWidth)
  );

  useEffect(() => {
    const handler = () => setBreakpoint(getBreakpoint(window.innerWidth));
    const mql = window.matchMedia('(min-width: 640px), (min-width: 1024px)');
    mql.addEventListener('change', handler);
    window.addEventListener('resize', handler);
    return () => {
      mql.removeEventListener('change', handler);
      window.removeEventListener('resize', handler);
    };
  }, []);

  return breakpoint;
}

export function useIsMobile(): boolean {
  return useBreakpoint() === 'mobile';
}

export function useIsTablet(): boolean {
  return useBreakpoint() === 'tablet';
}

export function useIsDesktop(): boolean {
  return useBreakpoint() === 'desktop';
}
