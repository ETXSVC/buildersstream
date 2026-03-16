import { useEffect } from 'react';
import { Hash, Lock, MessageCircle, Plus } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { listChannels, type Channel } from '@/api/collaboration';
import { useChatStore } from '@/stores/chat';

interface Props {
  onCreateChannel?: () => void;
  onNewDm?: () => void;
}

function ChannelItem({ channel }: { channel: Channel }) {
  const { activeChannelId, setActiveChannel } = useChatStore();
  const active = activeChannelId === channel.id;

  const Icon =
    channel.channel_type === 'direct'
      ? MessageCircle
      : channel.channel_type === 'private'
      ? Lock
      : Hash;

  return (
    <button
      type="button"
      onClick={() => setActiveChannel(channel.id)}
      className={`w-full flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
        active
          ? 'bg-indigo-600 text-white'
          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
      }`}
    >
      <Icon size={14} className="shrink-0" />
      <span className="truncate flex-1 text-left">
        {channel.channel_type === 'direct' ? 'Direct Message' : channel.name}
      </span>
      {channel.unread_count > 0 && (
        <span className="ml-auto bg-indigo-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[1.25rem] text-center">
          {channel.unread_count > 99 ? '99+' : channel.unread_count}
        </span>
      )}
    </button>
  );
}

export function ChatSidebar({ onCreateChannel, onNewDm }: Props) {
  const { setChannels, channels } = useChatStore();

  const { data } = useQuery({
    queryKey: ['collaboration', 'channels'],
    queryFn: listChannels,
    refetchInterval: 30_000,
  });

  useEffect(() => {
    if (data) setChannels(data);
  }, [data, setChannels]);

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
            <p className="px-4 text-xs text-gray-500 uppercase tracking-wider mb-1">
              Channels
            </p>
            {publicChannels.map((ch) => (
              <ChannelItem key={ch.id} channel={ch} />
            ))}
          </section>
        )}

        {privateChannels.length > 0 && (
          <section>
            <p className="px-4 text-xs text-gray-500 uppercase tracking-wider mb-1">
              Private
            </p>
            {privateChannels.map((ch) => (
              <ChannelItem key={ch.id} channel={ch} />
            ))}
          </section>
        )}

        <section>
          <div className="flex items-center justify-between px-4 mb-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">
              Direct Messages
            </p>
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
            <ChannelItem key={ch.id} channel={ch} />
          ))}
          {dms.length === 0 && (
            <p className="px-4 text-xs text-gray-600 italic">No direct messages yet.</p>
          )}
        </section>

      </nav>
    </aside>
  );
}
