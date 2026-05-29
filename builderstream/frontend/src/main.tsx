import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { useAuthStore } from './stores/auth';
import './index.css';
import 'frappe-gantt/dist/frappe-gantt.css';

// Silence react-router v6 deprecation warnings — we have opted in via RouterProvider future prop,
// but the library fires the warning from an internal component that doesn't receive the prop.
if (import.meta.env.DEV) {
  const _warn = console.warn.bind(console);
  console.warn = (...args: unknown[]) => {
    if (typeof args[0] === 'string' && args[0].includes('React Router Future Flag Warning')) return;
    _warn(...args);
  };
}

// Hydrate auth state from the bs_access cookie via /api/v1/users/me/profile/
useAuthStore.getState().hydrate();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
