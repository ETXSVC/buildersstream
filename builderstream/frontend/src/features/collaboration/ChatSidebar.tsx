import { useEffect, useState, useRef } from 'react';
import { Hash, Lock, MessageCircle, Plus, MoreHorizontal, Archive, RotateCcw, ChevronDown } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listChannels,
  listArchivedChannels,
  archiveChannel,
  unarchiveChannel,
  type Channel,
} from '@/api/collaboration';
import { useChatStore } from '@/stores/chat';

interface Props {
  onCreateChannel?: () => void;
  onNewDm?: () => void;
}

function ChannelMenu({
  channel,
  onArchive,
  onRestore,
}: {
  channel: Channel;
  onArchive?: () => void;
  onRestore?: () => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div ref={ref} className="relative ml-auto shrink-0">
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
        className="p-0.5 rounded text-gray-500 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
        title="Options"
      >
        <MoreHorizontal size={13} />
      </button>
      {open && (
        <div className="absolute right-0 top-6 z-50 w-36 rounded-lg bg-gray-900 border border-gray-700 shadow-xl py-1 text-sm">
          {onArchive && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setOpen(false); onArchive(); }}
              className="flex items-center gap-2 w-full px-3 py-1.5 text-gray-300 hover:bg-gray-700 hover:text-white"
            >
              <Archive size={13} />
              {channel.channel_type === 'direct' ? 'Close' : 'Archive'}
            </button>
          )}
          {onRestore && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setOpen(false); onRestore(); }}
              className="flex items-center gap-2 w-full px-3 py-1.5 text-gray-300 hover:bg-gray-700 hover:text-white"
            >
              <RotateCcw size={13} />
              Restore
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function ChannelItem({
  channel,
  onArchive,
  onRestore,
}: {
  channel: Channel;
  onArchive?: () => void;
  onRestore?: () => void;
}) {
  const { activeChannelId, setActiveChannel } = useChatStore();
  const active = activeChannelId === channel.id;

  const Icon =
    channel.channel_type === 'direct'
      ? MessageCircle
      : channel.channel_type === 'private'
      ? Lock
      : Hash;

  return (
    <div
      className={`group flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
        channel.is_archived
          ? 'text-gray-600 cursor-default'
          : active
          ? 'bg-indigo-600 text-white cursor-pointer'
          : 'text-gray-300 hover:bg-gray-700 hover:text-white cursor-pointer'
      }`}
      onClick={() => !channel.is_archived && setActiveChannel(channel.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && !channel.is_archived && setActiveChannel(channel.id)}
    >
      <Icon size={14} className="shrink-0" />
      <span className="truncate flex-1 text-sm text-left">
        {channel.channel_type === 'direct' ? 'Direct Message' : channel.name}
      </span>
      {channel.unread_count > 0 && !channel.is_archived && (
        <span className="bg-indigo-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[1.25rem] text-center">
          {channel.unread_count > 99 ? '99+' : channel.unread_count}
        </span>
      )}
      <ChannelMenu channel={channel} onArchive={onArchive} onRestore={onRestore} />
    </div>
  );
}

export function ChatSidebar({ onCreateChannel, onNewDm }: Props) {
  const qc = useQueryClient();
  const { setChannels, channels } = useChatStore();
  const [showArchived, setShowArchived] = useState(false);

  const { data } = useQuery({
    queryKey: ['collaboration', 'channels'],
    queryFn: listChannels,
    refetchInterval: 30_000,
  });

  const { data: archivedData = [] } = useQuery({
    queryKey: ['collaboration', 'channels', 'archived'],
    queryFn: listArchivedChannels,
    enabled: showArchived,
  });

  useEffect(() => {
    if (data) setChannels(data);
  }, [data, setChannels]);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['collaboration', 'channels'] });
    qc.invalidateQueries({ queryKey: ['collaboration', 'channels', 'archived'] });
  };

  const archiveMut = useMutation({ mutationFn: archiveChannel, onSuccess: invalidate });
  const unarchiveMut = useMutation({ mutationFn: unarchiveChannel, onSuccess: invalidate });

  const publicChannels = channels.filter((c) => c.channel_type === 'public');
  const privateChannels = channels.filter((c) => c.channel_type === 'private');
  const dms = channels.filter((c) => c.channel_type === 'direct');

  return (
    <aside className="w-56 bg-gray-800 flex flex-col h-full shrink-0">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
        <span className="text-white font-semibold text-sm">Team Chat</span>
        {onCreateChannel && (
          <button
            type="button"
            onClick={onCreateChannel}
            className="text-gray-400 hover:text-white"
            title="New channel"
          >
            <Plus size={16} />
          </button>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-2 space-y-4">
        {publicChannels.length > 0 && (
          <section>
            <p className="px-4 text-xs text-gray-500 uppercase tracking-wider mb-1">Channels</p>
            {publicChannels.map((ch) => (
              <ChannelItem key={ch.id} channel={ch} onArchive={() => archiveMut.mutate(ch.id)} />
            ))}
          </section>
        )}

        {privateChannels.length > 0 && (
          <section>
            <p className="px-4 text-xs text-gray-500 uppercase tracking-wider mb-1">Private</p>
            {privateChannels.map((ch) => (
              <ChannelItem key={ch.id} channel={ch} onArchive={() => archiveMut.mutate(ch.id)} />
            ))}
          </section>
        )}

        <section>
          <div className="flex items-center justify-between px-4 mb-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Direct Messages</p>
            {onNewDm && (
              <button
                type="button"
                onClick={onNewDm}
                className="text-gray-500 hover:text-white"
                title="New direct message"
              >
                <Plus size={13} />
              </button>
            )}
          </div>
          {dms.map((ch) => (
            <ChannelItem key={ch.id} channel={ch} onArchive={() => archiveMut.mutate(ch.id)} />
          ))}
          {dms.length === 0 && (
            <p className="px-4 text-xs text-gray-600 italic">No direct messages yet.</p>
          )}
        </section>

        {/* Archived section — collapsed by default */}
        <section>
          <button
            type="button"
            onClick={() => setShowArchived((v) => !v)}
            className="flex items-center gap-1.5 px-4 text-xs text-gray-600 hover:text-gray-400 uppercase tracking-wider w-full mb-1"
          >
            <ChevronDown size={11} className={`transition-transform ${showArchived ? '' : '-rotate-90'}`} />
            Archived
          </button>
          {showArchived && (
            archivedData.length === 0
              ? <p className="px-4 text-xs text-gray-600 italic">Nothing archived.</p>
              : archivedData.map((ch) => (
                  <ChannelItem
                    key={ch.id}
                    channel={ch}
                    onRestore={() => unarchiveMut.mutate(ch.id)}
                  />
                ))
          )}
        </section>
      </nav>
    </aside>
  );
}
