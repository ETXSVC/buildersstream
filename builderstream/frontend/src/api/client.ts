import axios from 'axios';
import type { TokenRefreshResponse } from '@/types/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

/** Raw client without interceptors — used for auth endpoints and token refresh. */
export const rawClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// --- Request interceptor: attach JWT + org header ---
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('bs_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const orgId = localStorage.getItem('bs_current_org');
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }
  return config;
});

// --- Response interceptor: auto-refresh on 401 ---
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (token) resolve(token);
    else reject(error);
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

    // No refresh token available — just reject (don't redirect)
    const refreshToken = localStorage.getItem('bs_refresh_token');
    if (!refreshToken) {
      return Promise.reject(error);
    }

    // If a refresh is already in flight, queue this request
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await rawClient.post<TokenRefreshResponse>(
        '/api/v1/auth/token/refresh/',
        { refresh: refreshToken },
      );

      localStorage.setItem('bs_access_token', data.access);
      localStorage.setItem('bs_refresh_token', data.refresh);

      processQueue(null, data.access);

      originalRequest.headers.Authorization = `Bearer ${data.access}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      clearAuth();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

function clearAuth() {
  localStorage.removeItem('bs_access_token');
  localStorage.removeItem('bs_refresh_token');
  localStorage.removeItem('bs_user');
  localStorage.removeItem('bs_organizations');
  localStorage.removeItem('bs_current_org');
  window.location.href = '/login';
}
