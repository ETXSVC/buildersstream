import { NavLink } from 'react-router-dom';

interface SubNavItem {
  label: string;
  to: string;
}

export function SubNav({ items }: { items: SubNavItem[] }) {
  return (
    <div className="flex gap-1 border-b border-slate-200 mb-6 -mt-1">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
              isActive
                ? 'border-amber-500 text-amber-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </div>
  );
}
