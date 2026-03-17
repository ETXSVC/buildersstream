import axios from 'axios';
// ESM circular imports are safe when accessed inside function bodies (not top-level).
// client.ts → useAuthStore → apiClient is fine: both modules are fully evaluated
// before any interceptor runs.
import { useAuthStore } from '@/stores/auth';

const API_URL = import.meta.env.VITE_API_URL || '';

// Tokens are stored in HttpOnly cookies set by the backend.
// withCredentials ensures the browser sends them automatically.
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

/** Raw client without interceptors — used for auth endpoints and token refresh. */
export const rawClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

// --- Request interceptor: attach org header from Zustand store ---
apiClient.interceptors.request.use((config) => {
  const orgId = useAuthStore.getState().currentOrganizationId;
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }
  return config;
});

// --- Response interceptor: refresh access token on 401, redirect to login if refresh fails ---
// During active use, a 401 means the 30-min access token expired; silently refresh it so the
// user's in-progress work isn't interrupted. A failed refresh (7-day refresh token expired)
// means the session is truly over → redirect to /login.
// Note: hydrate() uses rawClient (no interceptors) so page-load 401s — when the user returns
// after 30+ min idle — fall through to the catch block there and log the user out.
let isRefreshing = false;
let failedQueue: Array<{
  resolve: () => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve();
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise<void>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => apiClient(originalRequest));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // bs_refresh cookie sent automatically (withCredentials).
      // Backend sets a new bs_access cookie in the response.
      await rawClient.post('/api/v1/auth/token/refresh/', {});
      processQueue(null);
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError);
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);
