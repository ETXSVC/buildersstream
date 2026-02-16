import { create } from 'zustand';
import { authApi } from '@/api/auth';
import type { User, OrganizationMembership, LoginResponse } from '@/types/auth';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  organizations: OrganizationMembership[];
  currentOrganizationId: string | null;
  isAuthenticated: boolean;

  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => void;
  switchOrganization: (orgId: string) => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  organizations: [],
  currentOrganizationId: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const { data } = await authApi.login({ email, password });

    const currentOrgId =
      data.user.last_active_organization ||
      data.organizations[0]?.organization_id ||
      null;

    localStorage.setItem('bs_access_token', data.access);
    localStorage.setItem('bs_refresh_token', data.refresh);
    localStorage.setItem('bs_user', JSON.stringify(data.user));
    localStorage.setItem('bs_organizations', JSON.stringify(data.organizations));
    if (currentOrgId) {
      localStorage.setItem('bs_current_org', currentOrgId);
    }

    set({
      user: data.user,
      accessToken: data.access,
      refreshToken: data.refresh,
      organizations: data.organizations,
      currentOrganizationId: currentOrgId,
      isAuthenticated: true,
    });

    return data;
  },

  logout: () => {
    localStorage.removeItem('bs_access_token');
    localStorage.removeItem('bs_refresh_token');
    localStorage.removeItem('bs_user');
    localStorage.removeItem('bs_organizations');
    localStorage.removeItem('bs_current_org');

    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      organizations: [],
      currentOrganizationId: null,
      isAuthenticated: false,
    });
  },

  switchOrganization: (orgId) => {
    localStorage.setItem('bs_current_org', orgId);
    set({ currentOrganizationId: orgId });
  },

  hydrate: () => {
    const accessToken = localStorage.getItem('bs_access_token');
    const refreshToken = localStorage.getItem('bs_refresh_token');
    const userJson = localStorage.getItem('bs_user');
    const orgsJson = localStorage.getItem('bs_organizations');
    const currentOrgId = localStorage.getItem('bs_current_org');

    if (accessToken && refreshToken && userJson) {
      try {
        const user = JSON.parse(userJson) as User;
        const organizations = orgsJson
          ? (JSON.parse(orgsJson) as OrganizationMembership[])
          : [];

        set({
          user,
          accessToken,
          refreshToken,
          organizations,
          currentOrganizationId: currentOrgId,
          isAuthenticated: true,
        });
      } catch {
        // Corrupted localStorage — clear everything
        localStorage.removeItem('bs_access_token');
        localStorage.removeItem('bs_refresh_token');
        localStorage.removeItem('bs_user');
        localStorage.removeItem('bs_organizations');
        localStorage.removeItem('bs_current_org');
      }
    }
  },
}));
