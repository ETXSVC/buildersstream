export type TaskStatus = 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'canceled';
export type TaskType = 'task' | 'milestone' | 'summary' | 'deliverable';

export interface Task {
  id: string;
  project: string;
  project_name: string;
  name: string;
  task_type: TaskType;
  status: TaskStatus;
  start_date: string | null;
  end_date: string | null;
  duration_days: number | null;
  estimated_hours: number | null;
  actual_hours: number | null;
  completion_percentage: number;
  is_critical_path: boolean;
  float_days: number | null;
  assigned_crew: string | null;
  assigned_crew_name: string | null;
  parent_task: string | null;
  sort_order: number;
  wbs_code: string | null;
  color: string | null;
}

export interface Crew {
  id: string;
  name: string;
  trade: string;
  foreman: string | null;
  foreman_name: string | null;
  members: string[];
  member_count: number;
  hourly_rate: string | null;
  is_active: boolean;
}

export interface Equipment {
  id: string;
  name: string;
  equipment_type: string;
  make: string;
  model: string;
  year: number | null;
  serial_number: string;
  status: 'available' | 'in_use' | 'maintenance' | 'retired';
  is_available: boolean;
  daily_rate: string | null;
  daily_rental_rate: string | null;
  purchase_price: string | null;
  purchase_cost: string | null;
  current_book_value: string | null;
}

export interface GanttTask {
  id: string;
  name: string;
  wbs_code: string;
  task_type: TaskType;
  status: TaskStatus;
  start_date: string | null;
  end_date: string | null;
  completion_percentage: number;
  is_critical_path: boolean;
  float_days: number;
  assigned_crew: { id: string; name: string; trade: string } | null;
  estimated_hours: number | null;
  color: string | null;
  sort_order: number;
}

export interface GanttData {
  project_id: string;
  project_name: string;
  tasks: GanttTask[];
  milestones: GanttTask[];
  dependencies: { id: string; predecessor_id: string; successor_id: string; dependency_type: string; lag_days: number }[];
  crew_allocation: Record<string, Record<string, number>>;
  critical_path_task_ids: string[];
  stats: {
    total_tasks: number;
    completed_tasks: number;
    in_progress_tasks: number;
    on_hold_tasks: number;
    critical_path_tasks: number;
    average_completion_percentage: number;
    total_estimated_hours: number;
    total_actual_hours: number;
  };
}

export interface CrewAvailability {
  crew_id: string;
  crew_name: string;
  available_from: string | null;
  conflicts: string[];
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  not_started: 'bg-slate-100 text-slate-600',
  in_progress: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  on_hold: 'bg-blue-100 text-blue-700',
  canceled: 'bg-red-100 text-red-500',
};

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  not_started: 'Not Started',
  in_progress: 'In Progress',
  completed: 'Completed',
  on_hold: 'On Hold',
  canceled: 'Canceled',
};
