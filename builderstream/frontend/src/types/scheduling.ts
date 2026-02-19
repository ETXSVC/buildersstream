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
  percent_complete: number;
  is_critical_path: boolean;
  float_days: number | null;
  assigned_crew: string | null;
  assigned_crew_name: string | null;
  parent_task: string | null;
  sort_order: number;
  wbs_code: string | null;
}

export interface Crew {
  id: string;
  name: string;
  trade: string;
  foreman_name: string | null;
  size: number;
  hourly_rate: string | null;
  is_active: boolean;
}

export interface Equipment {
  id: string;
  name: string;
  equipment_type: string;
  make: string | null;
  model: string | null;
  year: number | null;
  is_available: boolean;
  daily_rate: string | null;
  purchase_price: string | null;
  current_book_value: string | null;
}

export interface GanttData {
  tasks: Task[];
  milestones: Task[];
  dependencies: { id: string; predecessor: string; successor: string; dependency_type: string }[];
  stats: {
    total_tasks: number;
    completed_tasks: number;
    critical_path_tasks: number;
    percent_complete: number;
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
  on_hold: 'bg-amber-100 text-amber-700',
  canceled: 'bg-red-100 text-red-500',
};

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  not_started: 'Not Started',
  in_progress: 'In Progress',
  completed: 'Completed',
  on_hold: 'On Hold',
  canceled: 'Canceled',
};
