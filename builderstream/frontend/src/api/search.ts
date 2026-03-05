import { apiClient } from './client';

export interface SearchResult {
  type: 'project' | 'contact' | 'lead' | 'estimate' | 'invoice' | 'document';
  id: string;
  title: string;
  subtitle: string;
  url: string;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
}

export async function universalSearch(q: string): Promise<SearchResponse> {
  const { data } = await apiClient.get('/api/v1/core/search/', { params: { q } });
  return data;
}
