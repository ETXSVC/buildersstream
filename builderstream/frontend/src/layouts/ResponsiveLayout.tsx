/**
 * ResponsiveLayout — selects MobileLayout, TabletLayout, or DesktopLayout
 * based on the current viewport breakpoint.
 */
import { useBreakpoint } from '@/hooks/useBreakpoint';
import { MobileLayout } from './MobileLayout';
import { TabletLayout } from './TabletLayout';
import { DesktopLayout } from './DesktopLayout';

export const ResponsiveLayout = () => {
  const breakpoint = useBreakpoint();

  if (breakpoint === 'mobile') return <MobileLayout />;
  if (breakpoint === 'tablet') return <TabletLayout />;
  return <DesktopLayout />;
};
