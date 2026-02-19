import { apiClient } from './client';
import type { ServiceRequest, Warranty, WarrantyClaim, DispatchBoard, ListResponse } from '@/types/service';

export const fetchServiceRequests = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<ServiceRequest>>('/api/v1/service/service-requests/', { params }).then((r) => r.data);

export const fetchWarranties = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Warranty>>('/api/v1/service/warranties/', { params }).then((r) => r.data);

export const fetchWarrantyClaims = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<WarrantyClaim>>('/api/v1/service/warranty-claims/', { params }).then((r) => r.data);

export const fetchDispatchBoard = (date: string) =>
  apiClient.get<DispatchBoard>('/api/v1/service/service-requests/dispatch/', { params: { date } }).then((r) => r.data);
