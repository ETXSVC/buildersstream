import type { ReactNode } from 'react';

interface WidgetCardProps {
  title: string;
  icon?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const WidgetCard = ({
  title,
  icon,
  action,
  children,
  className = '',
}: WidgetCardProps) => {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
        <div className="flex items-center gap-2">
          {icon && <span className="text-slate-600">{icon}</span>}
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
};
