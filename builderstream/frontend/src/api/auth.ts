import { rawClient } from './client';
import type { LoginRequest, LoginResponse, TokenRefreshResponse } from '@/types/auth';

export const authApi = {
  login: (data: LoginRequest) =>
    rawClient.post<LoginResponse>('/api/v1/auth/login/', data),

  refreshToken: (refresh: string) =>
    rawClient.post<TokenRefreshResponse>('/api/v1/auth/token/refresh/', {
      refresh,
    }),
};
