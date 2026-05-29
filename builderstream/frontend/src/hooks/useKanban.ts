import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchKanbanBoard } from '@/api/kanban';
import { updateProjectStatus } from '@/api/projects';

export function useKanbanBoard(showAll = false) {
  return useQuery({
    queryKey: ['kanban', showAll],
    queryFn: () => fetchKanbanBoard(showAll),
    staleTime: 30 * 1000,
  });
}

export function useKanbanMove() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, new_status }: { id: string; new_status: string }) =>
      updateProjectStatus(id, new_status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['kanban'] });
      qc.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
