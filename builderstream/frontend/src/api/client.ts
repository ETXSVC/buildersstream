import axios from 'axios';

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
  // Lazy import to avoid circular dependencies at module load time.
  const { useAuthStore } = require('@/stores/auth');
  const orgId = useAuthStore.getState().currentOrganizationId;
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }
  return config;
});

// --- Response interceptor: auto-refresh on 401 ---
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

    // If a refresh is already in flight, queue this request
    if (isRefreshing) {
      return new Promise<void>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => apiClient(originalRequest));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // The bs_refresh cookie is sent automatically (withCredentials).
      // Backend sets a new bs_access cookie in the response.
      await rawClient.post('/api/v1/auth/token/refresh/');
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
