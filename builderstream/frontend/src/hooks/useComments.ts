import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchComments, createComment, updateComment, deleteComment } from '@/api/comments';

export function useComments(projectId: string) {
  return useQuery({
    queryKey: ['comments', projectId],
    queryFn: () => fetchComments(projectId),
    staleTime: 30 * 1000,
  });
}

export function useCreateComment(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: { body: string; parent?: string }) =>
      createComment({ project: projectId, ...payload }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['comments', projectId] }),
  });
}

export function useUpdateComment(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) => updateComment(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['comments', projectId] }),
  });
}

export function useDeleteComment(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteComment(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['comments', projectId] }),
  });
}
