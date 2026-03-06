import { create } from 'zustand';
import type { Channel, Message } from '@/api/collaboration';

interface ChatState {
  channels: Channel[];
  activeChannelId: string | null;
  messages: Record<string, Message[]>; // channelId → messages
  wsMap: Record<string, WebSocket>;    // channelId → socket

  setChannels: (channels: Channel[]) => void;
  setActiveChannel: (channelId: string | null) => void;
  addMessage: (msg: Message) => void;
  updateMessage: (msg: Message) => void;
  deleteMessage: (channelId: string, msgId: string) => void;
  setMessages: (channelId: string, msgs: Message[]) => void;
  prependMessages: (channelId: string, msgs: Message[]) => void;
  decrementUnread: (channelId: string) => void;
  connectWs: (channelId: string) => void;
  disconnectWs: (channelId: string) => void;
  sendRaw: (channelId: string, payload: object) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  channels: [],
  activeChannelId: null,
  messages: {},
  wsMap: {},

  setChannels: (channels) => set({ channels }),

  setActiveChannel: (channelId) => set({ activeChannelId: channelId }),

  addMessage: (msg) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [msg.channel]: [...(state.messages[msg.channel] ?? []), msg],
      },
    })),

  updateMessage: (msg) =>
    set((state) => {
      const msgs = state.messages[msg.channel] ?? [];
      return {
        messages: {
          ...state.messages,
          [msg.channel]: msgs.map((m) => (m.id === msg.id ? msg : m)),
        },
      };
    }),

  deleteMessage: (channelId, msgId) =>
    set((state) => {
      const msgs = state.messages[channelId] ?? [];
      return {
        messages: {
          ...state.messages,
          [channelId]: msgs.map((m) =>
            m.id === msgId ? { ...m, is_deleted: true, content: '[deleted]' } : m
          ),
        },
      };
    }),

  setMessages: (channelId, msgs) =>
    set((state) => ({
      messages: { ...state.messages, [channelId]: msgs },
    })),

  prependMessages: (channelId, msgs) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [channelId]: [...msgs, ...(state.messages[channelId] ?? [])],
      },
    })),

  decrementUnread: (channelId) =>
    set((state) => ({
      channels: state.channels.map((ch) =>
        ch.id === channelId
          ? { ...ch, unread_count: 0 }
          : ch
      ),
    })),

  connectWs: (channelId) => {
    const { wsMap } = get();
    if (wsMap[channelId]) return; // already connected

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    // Auth is via the bs_access HttpOnly cookie sent automatically on WS upgrade.
    const url = `${proto}://${host}/ws/collaboration/channels/${channelId}/`;
    const ws = new WebSocket(url);

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string);
        const { addMessage, updateMessage, deleteMessage } = get();
        if (data.type === 'message.new') addMessage(data as Message);
        else if (data.type === 'message.edited') updateMessage(data as Message);
        else if (data.type === 'message.deleted')
          deleteMessage(channelId, data.message_id as string);
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      set((state) => {
        const next = { ...state.wsMap };
        delete next[channelId];
        return { wsMap: next };
      });
    };

    set((state) => ({
      wsMap: { ...state.wsMap, [channelId]: ws },
    }));
  },

  disconnectWs: (channelId) => {
    const { wsMap } = get();
    wsMap[channelId]?.close();
    set((state) => {
      const next = { ...state.wsMap };
      delete next[channelId];
      return { wsMap: next };
    });
  },

  sendRaw: (channelId, payload) => {
    const ws = get().wsMap[channelId];
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
    }
  },
}));
