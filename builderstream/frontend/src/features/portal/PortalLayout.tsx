import { useEffect, useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, CheckSquare, MessageCircle, Calendar, FileText, Image, Star, LogOut, Menu, X } from 'lucide-react';
import { clearPortalToken, getPortalToken, fetchPortalDashboard, type PortalBranding } from '@/api/portal';

const NAV = [
  { label: 'Overview', to: '/portal/dashboard', Icon: Home },
  { label: 'Approvals', to: '/portal/approvals', Icon: CheckSquare },
  { label: 'Selections', to: '/portal/selections', Icon: Star },
  { label: 'Messages', to: '/portal/messages', Icon: MessageCircle },
  { label: 'Schedule', to: '/portal/schedule', Icon: Calendar },
  { label: 'Documents', to: '/portal/documents', Icon: FileText },
  { label: 'Photos', to: '/portal/photos', Icon: Image },
];

export function PortalLayout() {
  const navigate = useNavigate();
  const [branding, setBranding] = useState<PortalBranding | null>(null);
  const [projectName, setProjectName] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!getPortalToken()) {
      navigate('/portal/login', { replace: true });
      return;
    }
    fetchPortalDashboard()
      .then((d) => {
        setBranding(d.branding);
        setProjectName(d.project.name);
      })
      .catch(() => {
        clearPortalToken();
        navigate('/portal/login', { replace: true });
      });
  }, [navigate]);

  const logout = () => {
    clearPortalToken();
    navigate('/portal/login', { replace: true });
  };

  const primaryColor = branding?.primary_color ?? '#3B82F6';
  const companyName = branding?.company_name ?? 'BuilderStream';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top bar */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {branding?.logo_url ? (
              <img src={branding.logo_url} alt={companyName} className="h-8 w-8 rounded-lg object-contain" />
            ) : (
              <div
                className="h-8 w-8 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                style={{ backgroundColor: primaryColor }}
              >
                {companyName.charAt(0)}
              </div>
            )}
            <div>
              <p className="text-sm font-semibold text-slate-900">{companyName}</p>
              {projectName && <p className="text-xs text-slate-500">{projectName}</p>}
            </div>
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV.map(({ label, to, Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`
                }
                style={({ isActive }) => isActive ? { backgroundColor: primaryColor } : {}}
              >
                <Icon size={13} />
                {label}
              </NavLink>
            ))}
            <button
              type="button"
              onClick={logout}
              className="ml-2 flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-500 hover:bg-slate-100"
            >
              <LogOut size={13} />
              Sign out
            </button>
          </nav>

          {/* Mobile menu toggle */}
          <button
            type="button"
            className="md:hidden text-slate-600"
            onClick={() => setMenuOpen((v) => !v)}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile nav */}
        {menuOpen && (
          <div className="md:hidden border-t border-slate-100 bg-white px-4 py-3 space-y-1">
            {NAV.map(({ label, to, Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                    isActive ? 'text-white' : 'text-slate-600 hover:bg-slate-100'
                  }`
                }
                style={({ isActive }) => isActive ? { backgroundColor: primaryColor } : {}}
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
            <button
              type="button"
              onClick={logout}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100"
            >
              <LogOut size={15} />
              Sign out
            </button>
          </div>
        )}
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
