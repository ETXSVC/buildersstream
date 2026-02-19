import { QuickClockInOut } from '@/components/mobile/QuickClockInOut';
import { useTimesheetSummary } from '@/hooks/useFieldOps';
import { PushNotificationManager } from '@/components/mobile/PushNotificationManager';

export const ClockPage = () => {
  const { data: summary } = useTimesheetSummary();

  return (
    <div className="flex flex-col items-center p-6 gap-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 text-center">Clock In / Out</h1>
        <p className="mt-1 text-sm text-slate-500 text-center">GPS-verified time tracking</p>
      </div>

      <QuickClockInOut />

      {/* This week summary */}
      {summary && (
        <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">This Week</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-slate-900">{Number(summary.regular_hours).toFixed(1)}</p>
              <p className="text-xs text-slate-500 mt-1">Regular hrs</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">{Number(summary.overtime_hours).toFixed(1)}</p>
              <p className="text-xs text-slate-500 mt-1">Overtime hrs</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{Number(summary.total_hours).toFixed(1)}</p>
              <p className="text-xs text-slate-500 mt-1">Total hrs</p>
            </div>
          </div>
        </div>
      )}

      {/* Push notifications */}
      <div className="w-full max-w-sm">
        <PushNotificationManager />
      </div>
    </div>
  );
};
