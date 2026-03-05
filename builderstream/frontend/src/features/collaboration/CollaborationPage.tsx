import { useEffect, useState } from 'react';
import { Hash } from 'lucide-react';
import { ChatSidebar } from './ChatSidebar';
import { MessageFeed } from './MessageFeed';
import { MessageComposer } from './MessageComposer';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import type { Message } from '@/api/collaboration';

export function CollaborationPage() {
  const { activeChannelId, channels, connectWs, disconnectWs } = useChatStore();
  const { accessToken } = useAuthStore();
  const [editingMessage, setEditingMessage] = useState<Message | null>(null);

  const activeChannel = channels.find((c) => c.id === activeChannelId);

  // Connect WebSocket when active channel changes
  useEffect(() => {
    if (!activeChannelId || !accessToken) return;
    connectWs(activeChannelId, accessToken);
    return () => disconnectWs(activeChannelId);
  }, [activeChannelId, accessToken, connectWs, disconnectWs]);

  // Clear editing when channel changes
  useEffect(() => {
    setEditingMessage(null);
  }, [activeChannelId]);

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-900">
      <ChatSidebar />

      {activeChannel ? (
        <main className="flex-1 flex flex-col min-w-0">
          {/* Channel header */}
          <header className="flex items-center gap-2 px-4 py-3 border-b border-gray-700 bg-gray-800 shrink-0">
            <Hash size={16} className="text-gray-400" />
            <span className="text-white font-semibold">
              {activeChannel.channel_type === 'direct'
                ? 'Direct Message'
                : activeChannel.name}
            </span>
            {activeChannel.description && (
              <>
                <span className="text-gray-600">|</span>
                <span className="text-sm text-gray-400 truncate">
                  {activeChannel.description}
                </span>
              </>
            )}
          </header>

          <MessageFeed
            channelId={activeChannelId!}
            onEditMessage={setEditingMessage}
          />

          <MessageComposer
            channelId={activeChannelId!}
            editingMessage={editingMessage}
            onCancelEdit={() => setEditingMessage(null)}
          />
        </main>
      ) : (
        <main className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <Hash size={48} className="mx-auto mb-4 opacity-30" />
            <p className="text-lg">Select a channel to start messaging</p>
          </div>
        </main>
      )}
    </div>
  );
}
