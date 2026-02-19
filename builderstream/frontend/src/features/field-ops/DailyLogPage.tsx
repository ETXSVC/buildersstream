import { useState } from 'react';
import { MobileDailyLog } from '@/components/mobile/MobileDailyLog';
import { useDailyLogs } from '@/hooks/useFieldOps';

export const DailyLogPage = () => {
  const today = new Date().toISOString().split('T')[0];
  const [selectedDate, setSelectedDate] = useState(today);
  const { data } = useDailyLogs({ log_date: selectedDate });

  const todayLog = data?.results[0] ?? null;

  return (
    <div className="p-4 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Daily Log</h1>
        <p className="mt-1 text-sm text-slate-500">Document daily site activities</p>
      </div>

      {/* Date picker */}
      <div className="flex items-center gap-2">
        <label htmlFor="log-date" className="text-sm text-slate-600">Date:</label>
        <input
          id="log-date"
          type="date"
          value={selectedDate}
          max={today}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-900 focus:border-amber-400 focus:outline-none"
        />
      </div>

      {/* Status badge if already submitted */}
      {todayLog && todayLog.status !== 'draft' && (
        <div className={`rounded-lg px-4 py-2 text-sm font-medium ${
          todayLog.status === 'approved'
            ? 'bg-green-50 text-green-700'
            : 'bg-amber-50 text-amber-700'
        }`}>
          Log {todayLog.status === 'approved' ? 'approved' : 'submitted'} — read only
        </div>
      )}

      {/* Mobile daily log form */}
      <MobileDailyLog />
    </div>
  );
};
