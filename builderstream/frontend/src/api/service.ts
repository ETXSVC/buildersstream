import { apiClient } from './client';
import type { ServiceRequest, Warranty, WarrantyClaim, DispatchBoard, ListResponse } from '@/types/service';

export const fetchServiceRequests = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<ServiceRequest>>('/api/v1/service/service-requests/', { params }).then((r) => r.data);

export const createServiceRequest = (payload: Record<string, unknown>) =>
  apiClient.post<ServiceRequest>('/api/v1/service/service-requests/', payload).then((r) => r.data);

export const updateServiceRequest = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<ServiceRequest>(`/api/v1/service/service-requests/${id}/`, payload).then((r) => r.data);

export const deleteServiceRequest = (id: string) =>
  apiClient.delete(`/api/v1/service/service-requests/${id}/`);

export const fetchWarranties = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<Warranty>>('/api/v1/service/warranties/', { params }).then((r) => r.data);

export const createWarranty = (payload: Record<string, unknown>) =>
  apiClient.post<Warranty>('/api/v1/service/warranties/', payload).then((r) => r.data);

export const updateWarranty = (id: string, payload: Record<string, unknown>) =>
  apiClient.patch<Warranty>(`/api/v1/service/warranties/${id}/`, payload).then((r) => r.data);

export const deleteWarranty = (id: string) =>
  apiClient.delete(`/api/v1/service/warranties/${id}/`);

export const fetchWarrantyClaims = (params?: Record<string, string>) =>
  apiClient.get<ListResponse<WarrantyClaim>>('/api/v1/service/warranty-claims/', { params }).then((r) => r.data);

export const fetchDispatchBoard = (date: string) =>
  apiClient.get<DispatchBoard>('/api/v1/service/service-requests/dispatch/', { params: { date } }).then((r) => r.data);
