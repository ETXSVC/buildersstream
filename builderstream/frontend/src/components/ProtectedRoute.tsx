import { useState, useCallback } from 'react';
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useIdleLogout } from '@/hooks/useIdleLogout';

function IdleWarningModal({
  onStay,
  onLogout,
}: {
  onStay: () => void;
  onLogout: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
          <svg className="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <h2 className="text-base font-semibold text-slate-900">Still there?</h2>
        <p className="mt-1.5 text-sm text-slate-500">
          You've been inactive for 28 minutes. You'll be signed out in{' '}
          <strong className="text-slate-800">2 minutes</strong> to protect your account.
        </p>
        <div className="mt-5 flex gap-3">
          <button
            type="button"
            onClick={onLogout}
            className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Sign out now
          </button>
          <button
            type="button"
            onClick={onStay}
            className="flex-1 rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600"
          >
            Stay signed in
          </button>
        </div>
      </div>
    </div>
  );
}

export const ProtectedRoute = () => {
  const { isAuthenticated, hydrating, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [showWarning, setShowWarning] = useState(false);

  const handleWarn = useCallback(() => {
    setShowWarning(true);
  }, []);

  const handleLogout = useCallback(async () => {
    setShowWarning(false);
    await logout();
    navigate('/login', { replace: true });
  }, [logout, navigate]);

  const handleStay = useCallback(() => {
    setShowWarning(false);
    // Activity events in the modal click already reset the idle timer
  }, []);

  useIdleLogout({
    enabled: isAuthenticated && !hydrating,
    onWarn: handleWarn,
    onLogout: handleLogout,
  });

  if (hydrating) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return (
    <>
      {showWarning && (
        <IdleWarningModal onStay={handleStay} onLogout={handleLogout} />
      )}
      <Outlet />
    </>
  );
};
