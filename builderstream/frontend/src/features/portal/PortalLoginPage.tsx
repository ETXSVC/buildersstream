import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { portalLogin, setPortalToken } from '@/api/portal';

export function PortalLoginPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [pin, setPin] = useState('');
  const [needsPin, setNeedsPin] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const token = params.get('token') ?? '';

  // Auto-login when token is in URL and no PIN needed
  useEffect(() => {
    if (!token) return;
    setLoading(true);
    portalLogin(token)
      .then((jwt) => {
        setPortalToken(jwt);
        navigate('/portal/dashboard', { replace: true });
      })
      .catch((err) => {
        setLoading(false);
        if (err?.response?.status === 403) {
          setNeedsPin(true);
        } else if (err?.response?.status === 401) {
          setError('This link has expired or is no longer valid. Please contact your contractor.');
        } else {
          setError('Unable to log in. Please try again or contact your contractor.');
        }
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const submitPin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pin.trim()) return;
    setLoading(true);
    setError('');
    try {
      const jwt = await portalLogin(token, pin);
      setPortalToken(jwt);
      navigate('/portal/dashboard', { replace: true });
    } catch {
      setLoading(false);
      setError('Incorrect PIN. Please try again.');
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="text-center">
          <div className="text-4xl mb-4">🔗</div>
          <h1 className="text-xl font-semibold text-slate-700 mb-2">No access link found</h1>
          <p className="text-slate-500 text-sm">Please use the link sent to your email to access the client portal.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent mx-auto mb-4" />
          <p className="text-slate-500 text-sm">Signing you in…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm text-center space-y-5">
        <div className="text-5xl">🏗️</div>
        <div>
          <h1 className="text-xl font-bold text-slate-900">Client Portal</h1>
          {needsPin && <p className="text-slate-500 text-sm mt-1">Enter your PIN to continue</p>}
        </div>

        {error && (
          <div className="rounded-xl bg-red-50 border border-red-200 p-3 text-sm text-red-700">{error}</div>
        )}

        {needsPin && (
          <form onSubmit={submitPin} className="space-y-4">
            <input
              autoFocus
              type="password"
              inputMode="numeric"
              maxLength={10}
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              placeholder="Enter PIN"
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-center text-lg tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 rounded-xl text-sm"
            >
              Access Portal
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
