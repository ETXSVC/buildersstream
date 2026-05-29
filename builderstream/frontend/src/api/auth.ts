import { rawClient } from './client';
import type { LoginRequest, LoginResponse } from '@/types/auth';

export const authApi = {
  login: (data: LoginRequest) =>
    rawClient.post<LoginResponse>('/api/v1/auth/login/', data),

  // Refresh token is in the bs_refresh HttpOnly cookie — no body needed.
  refreshToken: () =>
    rawClient.post('/api/v1/auth/token/refresh/'),

  // Clears bs_access and bs_refresh cookies server-side.
  logout: () =>
    rawClient.post('/api/v1/auth/logout/'),
};
