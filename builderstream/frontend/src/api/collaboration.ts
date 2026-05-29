import { apiClient } from './client';

export interface Channel {
  id: string;
  name: string;
  description: string;
  channel_type: 'public' | 'private' | 'direct';
  slug: string;
  project: string | null;
  is_archived: boolean;
  members_count: number;
  unread_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  channel: string;
  author: string | null;
  author_name: string | null;
  parent: string | null;
  content: string;
  is_edited: boolean;
  edited_at: string | null;
  is_deleted: boolean;
  attachments: unknown[];
  reactions: { emoji: string; count: number }[];
  reply_count: number;
  created_at: string;
  updated_at: string;
}

export async function listChannels(): Promise<Channel[]> {
  const { data } = await apiClient.get<{ results: Channel[] }>(
    '/api/v1/collaboration/channels/'
  );
  return data.results ?? (data as unknown as Channel[]);
}

export async function createChannel(payload: {
  name: string;
  description?: string;
  channel_type?: string;
  project?: string;
  member_ids?: string[];
}): Promise<Channel> {
  const { data } = await apiClient.post<Channel>(
    '/api/v1/collaboration/channels/',
    payload
  );
  return data;
}

export async function createDirectChannel(userId: string): Promise<Channel> {
  const { data } = await apiClient.post<Channel>(
    '/api/v1/collaboration/channels/direct/',
    { user_id: userId }
  );
  return data;
}

export async function listMessages(
  channelId: string,
  page = 1
): Promise<{ results: Message[]; count: number; next: string | null }> {
  const { data } = await apiClient.get(
    `/api/v1/collaboration/messages/?channel=${channelId}&page=${page}&ordering=created_at`
  );
  return data;
}

export async function markChannelRead(channelId: string): Promise<void> {
  await apiClient.post(`/api/v1/collaboration/channels/${channelId}/mark-read/`);
}

export async function joinChannel(channelId: string): Promise<void> {
  await apiClient.post(`/api/v1/collaboration/channels/${channelId}/join/`);
}

export async function leaveChannel(channelId: string): Promise<void> {
  await apiClient.post(`/api/v1/collaboration/channels/${channelId}/leave/`);
}

export async function archiveChannel(channelId: string): Promise<void> {
  await apiClient.post(`/api/v1/collaboration/channels/${channelId}/archive/`);
}

export async function unarchiveChannel(channelId: string): Promise<void> {
  await apiClient.post(`/api/v1/collaboration/channels/${channelId}/unarchive/`);
}

export async function listArchivedChannels(): Promise<Channel[]> {
  const { data } = await apiClient.get<{ results: Channel[] }>(
    '/api/v1/collaboration/channels/?is_archived=true'
  );
  return data.results ?? (data as unknown as Channel[]);
}
