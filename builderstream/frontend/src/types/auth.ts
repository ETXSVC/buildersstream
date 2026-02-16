export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar: string | null;
  job_title: string;
  email_verified: boolean;
  timezone: string;
  last_active_organization: string | null;
}

export interface OrganizationMembership {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  role:
    | 'owner'
    | 'admin'
    | 'project_manager'
    | 'estimator'
    | 'field_worker'
    | 'accountant'
    | 'read_only';
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
  organizations: OrganizationMembership[];
  warning?: string;
}

export interface TokenRefreshResponse {
  access: string;
  refresh: string;
}
