interface KpiCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: 'default' | 'green' | 'red' | 'amber' | 'blue' | 'indigo';
  icon?: string;
  onClick?: () => void;
}

const ACCENT_CLASSES: Record<NonNullable<KpiCardProps['accent']>, string> = {
  default: 'border-slate-100',
  green: 'border-green-200 bg-green-50',
  red: 'border-red-200 bg-red-50',
  amber: 'border-blue-200 bg-blue-50',
  blue: 'border-blue-200 bg-blue-50',
  indigo: 'border-indigo-200 bg-indigo-50',
};

const VALUE_CLASSES: Record<NonNullable<KpiCardProps['accent']>, string> = {
  default: 'text-slate-900',
  green: 'text-green-700',
  red: 'text-red-700',
  amber: 'text-blue-700',
  blue: 'text-blue-700',
  indigo: 'text-indigo-700',
};

export function KpiCard({ label, value, sub, accent = 'default', icon, onClick }: KpiCardProps) {
  return (
    <div
      className={`rounded-xl border bg-white p-5 shadow-sm ${ACCENT_CLASSES[accent]} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
    >
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
        {icon && <span className="text-xl">{icon}</span>}
      </div>
      <p className={`mt-2 text-2xl font-bold ${VALUE_CLASSES[accent]}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-400">{sub}</p>}
    </div>
  );
}
