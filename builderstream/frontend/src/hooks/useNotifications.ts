import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '@/stores/auth';

export interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  action_url: string | null;
  actor_name: string | null;
}

interface WsMessage {
  type: string;
  notifications?: Notification[];
  notification?: Notification;
  unread_count?: number;
  notification_id?: string;
}

export function useNotifications() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!isAuthenticated) return;
    // Auth is via the bs_access HttpOnly cookie sent automatically on WS upgrade.
    const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/notifications/`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      const msg: WsMessage = JSON.parse(event.data as string);
      if (msg.type === 'notification.list') {
        setNotifications(msg.notifications ?? []);
        setUnreadCount(msg.unread_count ?? 0);
      } else if (msg.type === 'notification.new') {
        if (msg.notification) {
          setNotifications((prev) => [msg.notification!, ...prev]);
          setUnreadCount((c) => c + 1);
        }
      } else if (msg.type === 'notification.read') {
        setNotifications((prev) =>
          prev.map((n) => (n.id === msg.notification_id ? { ...n, is_read: true } : n))
        );
        setUnreadCount((c) => Math.max(0, c - 1));
      } else if (msg.type === 'notification.all_read') {
        setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
        setUnreadCount(0);
      }
    };

    ws.onclose = (event) => {
      setConnected(false);
      // 4001 = auth rejected (expired/invalid token) — don't retry
      if (event.code === 4001) return;
      // Reconnect after 5s for any other close reason
      reconnectTimer.current = setTimeout(connect, 5000);
    };

    ws.onerror = () => ws.close();
  }, [isAuthenticated]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      // Only close if the socket has moved past CONNECTING (readyState 0).
      // Closing a CONNECTING socket in StrictMode dev double-mount produces a
      // harmless "closed before connection established" warning — guard it here.
      const ws = wsRef.current;
      if (ws && ws.readyState !== WebSocket.CONNECTING) {
        ws.close();
      } else if (ws) {
        ws.onopen = () => ws.close();
      }
    };
  }, [connect]);

  const markRead = useCallback((notificationId: string) => {
    wsRef.current?.send(JSON.stringify({ action: 'mark_read', notification_id: notificationId }));
  }, []);

  const markAllRead = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ action: 'mark_all_read' }));
  }, []);

  return { notifications, unreadCount, connected, markRead, markAllRead };
}
