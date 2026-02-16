import { useAuth } from '@/hooks/useAuth';

export const DashboardPage = () => {
  const { user, organizations, currentOrganizationId } = useAuth();
  const currentOrg = organizations.find(
    (o) => o.organization_id === currentOrganizationId,
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-navy-900">
        Welcome back, {user?.first_name}!
      </h1>
      {currentOrg && (
        <p className="mt-2 text-slate-600">
          {currentOrg.organization_name} &middot;{' '}
          <span className="capitalize">{currentOrg.role.replace('_', ' ')}</span>
        </p>
      )}
      <div className="mt-8 rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-slate-500">
          Your construction management dashboard is coming soon.
        </p>
      </div>
    </div>
  );
};
