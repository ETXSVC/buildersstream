import { useAuthStore } from '@/stores/auth';

export const useAuth = () => {
  const store = useAuthStore();
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    organizations: store.organizations,
    currentOrganizationId: store.currentOrganizationId,
    login: store.login,
    logout: store.logout,
    switchOrganization: store.switchOrganization,
  };
};
