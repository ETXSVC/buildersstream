declare module 'frappe-gantt' {
  export interface GanttTask {
    id: string;
    name: string;
    start: string;
    end: string;
    progress: number;
    dependencies?: string;
    custom_class?: string;
  }

  export interface GanttOptions {
    view_mode?: 'Hour' | 'Quarter Day' | 'Half Day' | 'Day' | 'Week' | 'Month';
    date_format?: string;
    popup_trigger?: 'click' | 'hover';
    on_click?: (task: GanttTask) => void;
    on_date_change?: (task: GanttTask, start: Date, end: Date) => void;
    on_progress_change?: (task: GanttTask, progress: number) => void;
    on_view_change?: (mode: string) => void;
  }

  export default class Gantt {
    constructor(
      element: HTMLElement | string,
      tasks: GanttTask[],
      options?: GanttOptions
    );
    change_view_mode(mode: string): void;
    refresh(tasks: GanttTask[]): void;
  }
}
