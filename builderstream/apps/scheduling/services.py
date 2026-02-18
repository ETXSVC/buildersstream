"""Scheduling services: critical path, conflict detection, Gantt data."""
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Q

from .models import Crew, Equipment, Task, TaskDependency


class CriticalPathService:
    """Calculate critical path using forward/backward pass (CPM)."""

    def __init__(self, project):
        self.project = project

    def calculate(self):
        """
        Run CPM forward/backward pass on all tasks in the project.
        Updates each task's early_start, early_finish, late_start, late_finish,
        float_days, and is_critical_path flag.
        Returns list of critical path task IDs.
        """
        tasks = list(
            Task.objects.filter(project=self.project)
            .exclude(status=Task.Status.CANCELED)
            .prefetch_related("predecessor_deps__predecessor", "successor_deps__successor")
        )
        if not tasks:
            return []

        # Build adjacency maps
        task_map = {t.id: t for t in tasks}
        successors: dict[Any, list] = defaultdict(list)  # task_id → [(dep, successor_task)]
        predecessors: dict[Any, list] = defaultdict(list)  # task_id → [(dep, pred_task)]

        deps = TaskDependency.objects.filter(
            predecessor__project=self.project
        ).select_related("predecessor", "successor")

        for dep in deps:
            if dep.predecessor_id in task_map and dep.successor_id in task_map:
                successors[dep.predecessor_id].append((dep, task_map[dep.successor_id]))
                predecessors[dep.successor_id].append((dep, task_map[dep.predecessor_id]))

        # Forward pass: compute early_start and early_finish
        today = date.today()
        for task in tasks:
            if not predecessors[task.id]:
                # No predecessors — start at scheduled start or today
                es = task.start_date or today
            else:
                es = today
                for dep, pred in predecessors[task.id]:
                    if dep.dependency_type == TaskDependency.DependencyType.FINISH_TO_START:
                        pred_finish = pred.early_finish or (pred.start_date or today) + timedelta(days=max(pred.duration_days - 1, 0))
                        candidate = pred_finish + timedelta(days=1 + dep.lag_days)
                    elif dep.dependency_type == TaskDependency.DependencyType.START_TO_START:
                        pred_start = pred.early_start or pred.start_date or today
                        candidate = pred_start + timedelta(days=dep.lag_days)
                    elif dep.dependency_type == TaskDependency.DependencyType.FINISH_TO_FINISH:
                        pred_finish = pred.early_finish or (pred.start_date or today) + timedelta(days=max(pred.duration_days - 1, 0))
                        candidate = pred_finish - timedelta(days=max(task.duration_days - 1, 0)) + timedelta(days=dep.lag_days)
                    else:  # START_TO_FINISH
                        pred_start = pred.early_start or pred.start_date or today
                        candidate = pred_start - timedelta(days=max(task.duration_days - 1, 0)) + timedelta(days=dep.lag_days)
                    if candidate > es:
                        es = candidate

            task.early_start = es
            task.early_finish = es + timedelta(days=max(task.duration_days - 1, 0))

        # Backward pass: compute late_start and late_finish
        # Find project end: maximum early_finish among all tasks
        project_end = max((t.early_finish for t in tasks if t.early_finish), default=today)

        for task in reversed(tasks):
            if not successors[task.id]:
                lf = project_end
            else:
                lf = project_end
                for dep, succ in successors[task.id]:
                    if dep.dependency_type == TaskDependency.DependencyType.FINISH_TO_START:
                        succ_start = succ.late_start or succ.early_start or today
                        candidate = succ_start - timedelta(days=1 + dep.lag_days)
                    elif dep.dependency_type == TaskDependency.DependencyType.START_TO_START:
                        succ_start = succ.late_start or succ.early_start or today
                        candidate = succ_start - timedelta(days=dep.lag_days) + timedelta(days=max(task.duration_days - 1, 0))
                    elif dep.dependency_type == TaskDependency.DependencyType.FINISH_TO_FINISH:
                        succ_finish = succ.late_finish or succ.early_finish or project_end
                        candidate = succ_finish - timedelta(days=dep.lag_days)
                    else:  # START_TO_FINISH
                        succ_finish = succ.late_finish or succ.early_finish or project_end
                        candidate = succ_finish + timedelta(days=max(task.duration_days - 1, 0)) - timedelta(days=dep.lag_days)
                    if candidate < lf:
                        lf = candidate

            task.late_finish = lf
            task.late_start = lf - timedelta(days=max(task.duration_days - 1, 0))

            # Float = late_start - early_start
            if task.early_start and task.late_start:
                task.float_days = (task.late_start - task.early_start).days
            else:
                task.float_days = 0

            task.is_critical_path = task.float_days <= 0

        # Bulk update
        Task.objects.bulk_update(
            tasks,
            ["early_start", "early_finish", "late_start", "late_finish", "float_days", "is_critical_path"],
        )

        critical_ids = [t.id for t in tasks if t.is_critical_path]
        return critical_ids

    def get_critical_path_tasks(self):
        """Return tasks on the critical path for this project."""
        return Task.objects.filter(project=self.project, is_critical_path=True).order_by("early_start")


class ScheduleConflictService:
    """Detect crew over-allocation and equipment double-booking."""

    def __init__(self, organization):
        self.organization = organization

    def detect_crew_conflicts(self, start_date=None, end_date=None):
        """
        Return list of crew conflicts: {crew, date, tasks, conflict_type}.
        A conflict occurs when a crew is assigned to overlapping tasks on the same day.
        """
        conflicts = []
        qs = Task.objects.filter(
            organization=self.organization,
            assigned_crew__isnull=False,
        ).exclude(status__in=[Task.Status.COMPLETED, Task.Status.CANCELED])

        if start_date:
            qs = qs.filter(end_date__gte=start_date)
        if end_date:
            qs = qs.filter(start_date__lte=end_date)

        # Group by crew
        crew_tasks: dict[Any, list] = defaultdict(list)
        for task in qs.select_related("assigned_crew", "project"):
            crew_tasks[task.assigned_crew_id].append(task)

        for crew_id, tasks in crew_tasks.items():
            if len(tasks) <= 1:
                continue
            # Check for overlapping date ranges
            for i, t1 in enumerate(tasks):
                for t2 in tasks[i + 1:]:
                    if t1.start_date and t1.end_date and t2.start_date and t2.end_date:
                        overlap_start = max(t1.start_date, t2.start_date)
                        overlap_end = min(t1.end_date, t2.end_date)
                        if overlap_start <= overlap_end:
                            conflicts.append({
                                "crew_id": str(crew_id),
                                "crew_name": t1.assigned_crew.name if t1.assigned_crew else "",
                                "conflict_type": "crew_overallocation",
                                "overlap_start": overlap_start,
                                "overlap_end": overlap_end,
                                "tasks": [
                                    {"id": str(t1.id), "name": t1.name, "project": t1.project.name},
                                    {"id": str(t2.id), "name": t2.name, "project": t2.project.name},
                                ],
                            })
        return conflicts

    def detect_equipment_conflicts(self, start_date=None, end_date=None):
        """
        Return list of equipment conflicts (double-booking).
        Equipment in IN_USE status should only be on one project.
        """
        conflicts = []
        equipment_qs = Equipment.objects.filter(
            organization=self.organization,
            status=Equipment.Status.IN_USE,
            current_project__isnull=False,
        )
        # Group by equipment to catch duplicates (shouldn't happen but check)
        seen = {}
        for equip in equipment_qs:
            if equip.id in seen:
                conflicts.append({
                    "equipment_id": str(equip.id),
                    "equipment_name": equip.name,
                    "conflict_type": "equipment_double_booking",
                    "projects": [str(seen[equip.id]), str(equip.current_project_id)],
                })
            seen[equip.id] = equip.current_project_id
        return conflicts

    def detect_all_conflicts(self, start_date=None, end_date=None):
        """Return combined list of all conflicts."""
        return {
            "crew_conflicts": self.detect_crew_conflicts(start_date, end_date),
            "equipment_conflicts": self.detect_equipment_conflicts(start_date, end_date),
        }


class GanttDataService:
    """Build Gantt chart data structure for a project."""

    def __init__(self, project):
        self.project = project

    def get_gantt_data(self):
        """
        Return complete Gantt data structure including tasks, dependencies,
        milestones, and crew allocation.
        """
        tasks = list(
            Task.objects.filter(project=self.project)
            .select_related("assigned_crew", "parent_task", "cost_code")
            .prefetch_related("assigned_users", "successor_deps")
            .order_by("sort_order", "start_date")
        )
        deps = list(
            TaskDependency.objects.filter(predecessor__project=self.project)
            .select_related("predecessor", "successor")
        )

        # Build task list
        task_data = []
        milestone_data = []
        for task in tasks:
            entry = {
                "id": str(task.id),
                "name": task.name,
                "wbs_code": task.wbs_code,
                "task_type": task.task_type,
                "status": task.status,
                "parent_id": str(task.parent_task_id) if task.parent_task_id else None,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "actual_start": task.actual_start.isoformat() if task.actual_start else None,
                "actual_end": task.actual_end.isoformat() if task.actual_end else None,
                "duration_days": task.duration_days,
                "completion_percentage": task.completion_percentage,
                "is_critical_path": task.is_critical_path,
                "float_days": task.float_days,
                "early_start": task.early_start.isoformat() if task.early_start else None,
                "early_finish": task.early_finish.isoformat() if task.early_finish else None,
                "late_start": task.late_start.isoformat() if task.late_start else None,
                "late_finish": task.late_finish.isoformat() if task.late_finish else None,
                "assigned_crew": {
                    "id": str(task.assigned_crew.id),
                    "name": task.assigned_crew.name,
                    "trade": task.assigned_crew.trade,
                } if task.assigned_crew else None,
                "assigned_users": [str(u.id) for u in task.assigned_users.all()],
                "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                "actual_hours": float(task.actual_hours),
                "color": task.color,
                "sort_order": task.sort_order,
            }
            if task.task_type == Task.TaskType.MILESTONE:
                milestone_data.append(entry)
            else:
                task_data.append(entry)

        # Build dependencies
        dep_data = [
            {
                "id": str(dep.id),
                "predecessor_id": str(dep.predecessor_id),
                "successor_id": str(dep.successor_id),
                "dependency_type": dep.dependency_type,
                "lag_days": dep.lag_days,
            }
            for dep in deps
        ]

        # Crew allocation heat map: crew → date → hours
        crew_allocation = self._build_crew_allocation(tasks)

        return {
            "project_id": str(self.project.id),
            "project_name": self.project.name,
            "tasks": task_data,
            "milestones": milestone_data,
            "dependencies": dep_data,
            "crew_allocation": crew_allocation,
            "critical_path_task_ids": [
                str(t.id) for t in tasks if t.is_critical_path
            ],
            "stats": self._compute_stats(tasks),
        }

    def _build_crew_allocation(self, tasks):
        """Build crew allocation heat map by date."""
        allocation: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for task in tasks:
            if not task.assigned_crew or not task.start_date or not task.end_date:
                continue
            if task.status in (Task.Status.CANCELED, Task.Status.COMPLETED):
                continue
            crew_key = str(task.assigned_crew_id)
            current = task.start_date
            while current <= task.end_date:
                daily_hours = float(task.estimated_hours or 8) / max(task.duration_days, 1)
                allocation[crew_key][current.isoformat()] += daily_hours
                current += timedelta(days=1)
        # Convert nested defaultdicts to regular dicts
        return {k: dict(v) for k, v in allocation.items()}

    def _compute_stats(self, tasks):
        """Compute summary statistics."""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == Task.Status.COMPLETED)
        in_progress = sum(1 for t in tasks if t.status == Task.Status.IN_PROGRESS)
        on_hold = sum(1 for t in tasks if t.status == Task.Status.ON_HOLD)
        critical = sum(1 for t in tasks if t.is_critical_path)
        avg_completion = (
            sum(t.completion_percentage for t in tasks) / total if total else 0
        )
        total_est_hours = sum(
            float(t.estimated_hours) for t in tasks if t.estimated_hours
        )
        total_actual_hours = sum(float(t.actual_hours) for t in tasks)
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "on_hold_tasks": on_hold,
            "critical_path_tasks": critical,
            "average_completion_percentage": round(avg_completion, 1),
            "total_estimated_hours": round(total_est_hours, 2),
            "total_actual_hours": round(total_actual_hours, 2),
        }
