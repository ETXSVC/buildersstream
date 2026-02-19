import { useQuery } from '@tanstack/react-query';
import { fetchServiceRequests, fetchWarranties, fetchWarrantyClaims, fetchDispatchBoard } from '@/api/service';

export const useServiceRequests = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['service-requests', params],
    queryFn: () => fetchServiceRequests(params),
    staleTime: 30_000,
  });

export const useWarranties = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['warranties', params],
    queryFn: () => fetchWarranties(params),
    staleTime: 30_000,
  });

export const useWarrantyClaims = (params?: Record<string, string>) =>
  useQuery({
    queryKey: ['warranty-claims', params],
    queryFn: () => fetchWarrantyClaims(params),
    staleTime: 30_000,
  });

export const useDispatchBoard = (date: string) =>
  useQuery({
    queryKey: ['dispatch-board', date],
    queryFn: () => fetchDispatchBoard(date),
    staleTime: 30_000,
    enabled: !!date,
  });
