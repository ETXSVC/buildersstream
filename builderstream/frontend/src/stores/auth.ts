import { create } from 'zustand';
import { authApi } from '@/api/auth';
import { apiClient } from '@/api/client';
import type { User, OrganizationMembership, LoginResponse } from '@/types/auth';

interface AuthState {
  user: User | null;
  organizations: OrganizationMembership[];
  currentOrganizationId: string | null;
  isAuthenticated: boolean;

  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  switchOrganization: (orgId: string) => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  organizations: [],
  currentOrganizationId: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const { data } = await authApi.login({ email, password });

    const currentOrgId =
      data.user.last_active_organization ||
      data.organizations[0]?.organization_id ||
      null;

    // Tokens are stored in HttpOnly cookies by the backend — never in JS storage.
    set({
      user: data.user,
      organizations: data.organizations,
      currentOrganizationId: currentOrgId,
      isAuthenticated: true,
    });

    return data;
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Cookie clearing is server-side; ignore network errors
    }
    set({
      user: null,
      organizations: [],
      currentOrganizationId: null,
      isAuthenticated: false,
    });
  },

  switchOrganization: (orgId) => {
    set({ currentOrganizationId: orgId });
  },

  hydrate: async () => {
    // 'bs_access' cookie is sent automatically via withCredentials.
    // 401 → stay unauthenticated; 200 → restore session from backend.
    try {
      const { data } = await apiClient.get<{
        user: User;
        organizations: OrganizationMembership[];
      }>('/api/v1/users/me/profile/');

      const currentOrgId =
        data.user.last_active_organization ||
        data.organizations[0]?.organization_id ||
        null;

      set({
        user: data.user,
        organizations: data.organizations,
        currentOrganizationId: currentOrgId,
        isAuthenticated: true,
      });
    } catch {
      set({ isAuthenticated: false });
    }
  },
}));
