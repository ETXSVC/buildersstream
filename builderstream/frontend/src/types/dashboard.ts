/**
 * Dashboard data types matching backend API responses
 */

export interface ProjectMetrics {
  total_projects: number;
  active_projects: number;
  on_hold_projects: number;
  completed_projects: number;
  health_distribution: {
    green: number;
    yellow: number;
    red: number;
  };
  by_status: Record<string, number>;
}

export interface FinancialSummary {
  monthly_revenue: string; // Decimal as string
  monthly_costs: string;
  total_budget: string;
  budget_utilized: string;
  budget_utilization_pct: string;
  upcoming_invoices_count: number;
  upcoming_invoices_total: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  project_name: string;
  name: string;
  due_date: string; // ISO date string
  status: string;
  is_overdue: boolean;
}

export interface CrewAvailability {
  crew_name: string;
  available: number;
  total: number;
  utilization_pct: string;
}

export interface ScheduleOverview {
  upcoming_milestones: Milestone[];
  overdue_tasks_count: number;
  crew_availability: CrewAvailability[];
}

export interface ActionItem {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date: string | null;
  assigned_to: string | null;
  assigned_to_name: string | null;
  project_id: string | null;
  project_name: string | null;
  item_type: string;
  status: string;
  created_at: string;
}

export interface ActivityLogEntry {
  id: string;
  user_name: string;
  action: string;
  entity_type: string;
  entity_id: string;
  description: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface DashboardData {
  organization_id: string;
  organization_name: string;
  project_metrics: ProjectMetrics;
  financial_summary: FinancialSummary;
  schedule_overview: ScheduleOverview;
  action_items: ActionItem[];
  activity_stream: ActivityLogEntry[];
  user_role: string;
  cached_at: string | null;
}

export interface Widget {
  id: string;
  type: 'projects' | 'financial' | 'schedule' | 'actions' | 'activity';
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
  isVisible: boolean;
}

export interface DashboardLayout {
  widgets: Widget[];
  updated_at: string;
}

export interface DashboardLayoutPayload {
  widgets: Omit<Widget, 'id' | 'title'>[];
}
