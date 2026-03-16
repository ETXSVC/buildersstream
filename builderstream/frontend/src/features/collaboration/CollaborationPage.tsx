import { useEffect, useRef, useState } from 'react';
import { Hash } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ChatSidebar } from './ChatSidebar';
import { MessageFeed } from './MessageFeed';
import { MessageComposer } from './MessageComposer';
import { useChatStore } from '@/stores/chat';
import { createChannel } from '@/api/collaboration';
import type { Message } from '@/api/collaboration';

function CreateChannelModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const nameRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [channelType, setChannelType] = useState<'public' | 'private'>('public');

  const mutation = useMutation({
    mutationFn: createChannel,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['collaboration', 'channels'] });
      onClose();
    },
  });

  useEffect(() => { nameRef.current?.focus(); }, []);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    mutation.mutate({ name: name.trim(), description: description.trim(), channel_type: channelType });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={submit}
        className="bg-gray-800 rounded-xl p-6 w-full max-w-sm space-y-4 shadow-2xl"
      >
        <h2 className="text-white font-semibold text-lg">Create Channel</h2>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Channel name</label>
          <input
            ref={nameRef}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. general"
            className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Description (optional)</label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What is this channel for?"
            className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex gap-3">
          {(['public', 'private'] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setChannelType(t)}
              className={`flex-1 py-1.5 rounded text-sm font-medium transition-colors ${
                channelType === t
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
        {mutation.isError && (
          <p className="text-xs text-red-400">Failed to create channel.</p>
        )}
        <div className="flex justify-end gap-2 pt-1">
          <button type="button" onClick={onClose} className="px-4 py-1.5 rounded text-sm text-gray-300 hover:text-white">
            Cancel
          </button>
          <button
            type="submit"
            disabled={!name.trim() || mutation.isPending}
            className="px-4 py-1.5 rounded text-sm bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {mutation.isPending ? 'Creating…' : 'Create'}
          </button>
        </div>
      </form>
    </div>
  );
}

export function CollaborationPage() {
  const { activeChannelId, channels, connectWs, disconnectWs } = useChatStore();
  const [editingMessage, setEditingMessage] = useState<Message | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const activeChannel = channels.find((c) => c.id === activeChannelId);

  // Connect WebSocket when active channel changes.
  // Auth is via the bs_access HttpOnly cookie — no token param needed.
  useEffect(() => {
    if (!activeChannelId) return;
    connectWs(activeChannelId);
    return () => disconnectWs(activeChannelId);
  }, [activeChannelId, connectWs, disconnectWs]);

  // Clear editing when channel changes
  useEffect(() => {
    setEditingMessage(null);
  }, [activeChannelId]);

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-900">
      {showCreate && <CreateChannelModal onClose={() => setShowCreate(false)} />}
      <ChatSidebar onCreateChannel={() => setShowCreate(true)} />

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
