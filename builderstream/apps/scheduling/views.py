"""Scheduling views: Gantt, crews, equipment, critical path."""
from datetime import date, timedelta

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember
from apps.tenants.context import get_current_organization

from .models import Crew, Equipment, Task, TaskDependency
from .serializers import (
    CrewAvailabilitySerializer,
    CrewSerializer,
    EquipmentSerializer,
    GanttDataSerializer,
    TaskDependencySerializer,
    TaskListSerializer,
    TaskSerializer,
)
from .services import CriticalPathService, GanttDataService, ScheduleConflictService


class CrewViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for work crews + availability endpoint."""

    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_active", "trade"]
    search_fields = ["name"]

    @action(detail=False, methods=["get"], url_path="availability")
    def availability(self, request):
        """
        Return crew allocation across all projects for a date range.
        Query params: start_date, end_date (ISO format), crew_ids (comma-separated)
        """
        from collections import defaultdict

        start_str = request.query_params.get("start_date")
        end_str = request.query_params.get("end_date")
        crew_ids_str = request.query_params.get("crew_ids", "")

        try:
            start = date.fromisoformat(start_str) if start_str else date.today()
            end = date.fromisoformat(end_str) if end_str else start + timedelta(days=30)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use ISO format (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        org = get_current_organization()
        crews_qs = Crew.objects.filter(organization=org, is_active=True)
        if crew_ids_str:
            crew_ids = [cid.strip() for cid in crew_ids_str.split(",") if cid.strip()]
            crews_qs = crews_qs.filter(id__in=crew_ids)

        tasks_qs = Task.objects.filter(
            organization=org,
            assigned_crew__isnull=False,
            start_date__lte=end,
            end_date__gte=start,
        ).exclude(status__in=[Task.Status.CANCELED, Task.Status.COMPLETED]).select_related(
            "assigned_crew", "project"
        )

        # Build allocation map
        crew_tasks = defaultdict(list)
        for task in tasks_qs:
            crew_tasks[task.assigned_crew_id].append(task)

        result = []
        for crew in crews_qs:
            tasks = crew_tasks.get(crew.id, [])
            allocation_by_date = defaultdict(float)
            for task in tasks:
                t_start = max(task.start_date or start, start)
                t_end = min(task.end_date or end, end)
                if t_start > t_end:
                    continue
                days = (t_end - t_start).days + 1
                daily_hours = float(task.estimated_hours or 8) / max(task.duration_days, 1)
                current = t_start
                while current <= t_end:
                    allocation_by_date[current.isoformat()] += daily_hours
                    current += timedelta(days=1)

            is_overallocated = any(h > 10 for h in allocation_by_date.values())

            result.append({
                "crew_id": crew.id,
                "crew_name": crew.name,
                "trade": crew.trade,
                "allocation_by_date": dict(allocation_by_date),
                "allocated_tasks": [
                    {
                        "id": str(t.id),
                        "name": t.name,
                        "project": t.project.name,
                        "start_date": t.start_date.isoformat() if t.start_date else None,
                        "end_date": t.end_date.isoformat() if t.end_date else None,
                    }
                    for t in tasks
                ],
                "is_overallocated": is_overallocated,
            })

        return Response(result)


class TaskViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Full CRUD for scheduling tasks with Gantt + critical path actions."""

    queryset = Task.objects.select_related(
        "project", "parent_task", "assigned_crew", "cost_code"
    ).prefetch_related("assigned_users", "predecessor_deps", "successor_deps")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "task_type", "assigned_crew", "is_critical_path"]
    search_fields = ["name", "wbs_code"]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        return TaskSerializer

    @action(detail=False, methods=["get"], url_path="gantt")
    def gantt(self, request):
        """Return full Gantt chart data for a project."""
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response(
                {"error": "project_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from apps.projects.models import Project
            org = get_current_organization()
            project = Project.objects.get(id=project_id, organization=org)
        except Exception:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        service = GanttDataService(project)
        data = service.get_gantt_data()
        return Response(data)

    @action(detail=False, methods=["post"], url_path="calculate-critical-path")
    def calculate_critical_path(self, request):
        """Run CPM algorithm for a project and return critical path task IDs."""
        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"error": "project_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from apps.projects.models import Project
            org = get_current_organization()
            project = Project.objects.get(id=project_id, organization=org)
        except Exception:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        service = CriticalPathService(project)
        critical_ids = service.calculate()
        return Response({
            "project_id": str(project.id),
            "critical_path_task_ids": [str(i) for i in critical_ids],
            "critical_task_count": len(critical_ids),
        })

    @action(detail=False, methods=["get"], url_path="conflicts")
    def conflicts(self, request):
        """Return all schedule conflicts (crew overallocation, equipment double-booking)."""
        start_str = request.query_params.get("start_date")
        end_str = request.query_params.get("end_date")
        start = date.fromisoformat(start_str) if start_str else None
        end = date.fromisoformat(end_str) if end_str else None

        org = get_current_organization()
        service = ScheduleConflictService(org)
        conflicts = service.detect_all_conflicts(start, end)
        return Response(conflicts)

    @action(detail=True, methods=["post"], url_path="add-dependency")
    def add_dependency(self, request, pk=None):
        """Add a task dependency."""
        task = self.get_object()
        successor_id = request.data.get("successor_id")
        dep_type = request.data.get("dependency_type", TaskDependency.DependencyType.FINISH_TO_START)
        lag_days = int(request.data.get("lag_days", 0))

        if not successor_id:
            return Response({"error": "successor_id required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            org = get_current_organization()
            successor = Task.objects.get(id=successor_id, organization=org)
        except Task.DoesNotExist:
            return Response({"error": "Successor task not found."}, status=status.HTTP_404_NOT_FOUND)

        if successor == task:
            return Response({"error": "A task cannot depend on itself."}, status=status.HTTP_400_BAD_REQUEST)

        dep, created = TaskDependency.objects.get_or_create(
            predecessor=task,
            successor=successor,
            defaults={"dependency_type": dep_type, "lag_days": lag_days},
        )
        serializer = TaskDependencySerializer(dep)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="update-progress")
    def update_progress(self, request, pk=None):
        """Update task completion percentage and status."""
        task = self.get_object()
        completion = request.data.get("completion_percentage")
        new_status = request.data.get("status")

        if completion is not None:
            completion = int(completion)
            if not 0 <= completion <= 100:
                return Response(
                    {"error": "completion_percentage must be 0-100."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            task.completion_percentage = completion
            if completion == 100:
                task.status = Task.Status.COMPLETED
                if not task.actual_end:
                    task.actual_end = date.today()
            elif completion > 0 and task.status == Task.Status.NOT_STARTED:
                task.status = Task.Status.IN_PROGRESS
                if not task.actual_start:
                    task.actual_start = date.today()

        if new_status and new_status in Task.Status.values:
            task.status = new_status

        task.save()
        return Response(TaskSerializer(task).data)


class TaskDependencyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for task dependencies."""

    queryset = TaskDependency.objects.select_related("predecessor", "successor")
    serializer_class = TaskDependencySerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["dependency_type"]

    def get_queryset(self):
        org = get_current_organization()
        return TaskDependency.objects.filter(
            predecessor__organization=org
        ).select_related("predecessor", "successor")

    def perform_create(self, serializer):
        serializer.save()


class EquipmentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for equipment + depreciation calculation."""

    queryset = Equipment.objects.select_related("current_project")
    serializer_class = EquipmentSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "equipment_type", "current_project"]
    search_fields = ["name", "serial_number", "equipment_type"]

    @action(detail=True, methods=["get"], url_path="depreciation")
    def depreciation(self, request, pk=None):
        """Return depreciation schedule and current book value."""
        equipment = self.get_object()
        book_value = equipment.calculate_book_value()
        purchase_cost = float(equipment.purchase_cost or 0)
        data = {
            "equipment_id": equipment.id,
            "name": equipment.name,
            "purchase_cost": equipment.purchase_cost,
            "purchase_date": equipment.purchase_date,
            "depreciation_method": equipment.depreciation_method,
            "useful_life_years": equipment.useful_life_years,
            "salvage_value": equipment.salvage_value,
            "current_book_value": equipment.current_book_value,
            "net_book_value": book_value,
            "accumulated_depreciation": purchase_cost - book_value,
        }
        return Response(data)

    @action(detail=False, methods=["post"], url_path="update-all-book-values")
    def update_all_book_values(self, request):
        """Recalculate and save book values for all active equipment."""
        org = get_current_organization()
        equipment_list = Equipment.objects.filter(organization=org).exclude(
            status=Equipment.Status.RETIRED
        )
        updated = 0
        for equip in equipment_list:
            new_value = equip.calculate_book_value()
            if new_value != float(equip.current_book_value):
                equip.current_book_value = new_value
                equip.save(update_fields=["current_book_value"])
                updated += 1
        return Response({"updated_count": updated})
