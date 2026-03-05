import { useEffect, useRef, useState } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { listMessages, markChannelRead, type Message } from '@/api/collaboration';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import { Pencil, Trash2, SmilePlus } from 'lucide-react';

const COMMON_EMOJI = ['👍', '❤️', '😂', '🎉', '👀', '🚀'];

function MessageBubble({
  msg,
  onReact,
  onEdit,
  onDelete,
  isMine,
}: {
  msg: Message;
  onReact: (emoji: string) => void;
  onEdit: () => void;
  onDelete: () => void;
  isMine: boolean;
}) {
  const [showPicker, setShowPicker] = useState(false);

  if (msg.is_deleted) {
    return (
      <div className="px-4 py-1 text-sm italic text-gray-500">
        [deleted]
      </div>
    );
  }

  const groupedReactions = msg.reactions.reduce<Record<string, number>>(
    (acc, r) => ({ ...acc, [r.emoji]: r.count }),
    {}
  );

  return (
    <div className="group px-4 py-1 hover:bg-gray-750 relative">
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-xs font-bold shrink-0 mt-0.5">
          {(msg.author_name ?? '?')[0].toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-semibold text-gray-200">
              {msg.author_name ?? 'Unknown'}
            </span>
            <span className="text-xs text-gray-500">
              {new Date(msg.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            {msg.is_edited && (
              <span className="text-xs text-gray-500">(edited)</span>
            )}
          </div>
          <p className="text-sm text-gray-300 whitespace-pre-wrap break-words">
            {msg.content}
          </p>
          {Object.entries(groupedReactions).length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {Object.entries(groupedReactions).map(([emoji, count]) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => onReact(emoji)}
                  className="bg-gray-700 hover:bg-gray-600 rounded-full px-2 py-0.5 text-xs flex items-center gap-1"
                >
                  {emoji} <span className="text-gray-400">{count}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Action buttons — visible on hover */}
        <div className="hidden group-hover:flex items-center gap-1 shrink-0">
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowPicker((v) => !v)}
              className="p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded"
              title="React"
            >
              <SmilePlus size={14} />
            </button>
            {showPicker && (
              <div className="absolute right-0 top-6 bg-gray-800 border border-gray-600 rounded shadow-lg p-1 flex gap-1 z-10">
                {COMMON_EMOJI.map((e) => (
                  <button
                    key={e}
                    type="button"
                    onClick={() => {
                      onReact(e);
                      setShowPicker(false);
                    }}
                    className="hover:bg-gray-700 p-1 rounded text-base"
                  >
                    {e}
                  </button>
                ))}
              </div>
            )}
          </div>
          {isMine && (
            <>
              <button
                type="button"
                onClick={onEdit}
                className="p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded"
                title="Edit"
              >
                <Pencil size={14} />
              </button>
              <button
                type="button"
                onClick={onDelete}
                className="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded"
                title="Delete"
              >
                <Trash2 size={14} />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

interface Props {
  channelId: string;
  onEditMessage?: (msg: Message) => void;
}

export function MessageFeed({ channelId, onEditMessage }: Props) {
  const { messages, setMessages, prependMessages, decrementUnread, sendRaw } =
    useChatStore();
  const { user } = useAuthStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ['collaboration', 'messages', channelId],
      queryFn: ({ pageParam = 1 }) => listMessages(channelId, pageParam as number),
      getNextPageParam: (last, pages) =>
        last.next ? pages.length + 1 : undefined,
      initialPageParam: 1,
    });

  // Load first page into store
  useEffect(() => {
    if (data?.pages[0]) {
      setMessages(channelId, data.pages[0].results);
    }
  }, [data?.pages, channelId, setMessages]);

  // Prepend older pages
  useEffect(() => {
    if (data && data.pages.length > 1) {
      const older = data.pages
        .slice(1)
        .flatMap((p) => p.results)
        .reverse();
      prependMessages(channelId, older);
    }
  }, [data?.pages.length, channelId]); // eslint-disable-line

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (isAtBottom) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages[channelId]?.length, isAtBottom]);

  // Mark read when channel is viewed
  useEffect(() => {
    markChannelRead(channelId).catch(() => {});
    decrementUnread(channelId);
  }, [channelId, decrementUnread]);

  const channelMsgs = messages[channelId] ?? [];

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    setIsAtBottom(atBottom);
    if (el.scrollTop < 50 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  };

  const handleReact = (msg: Message, emoji: string) => {
    sendRaw(channelId, {
      type: 'reaction.toggle',
      message_id: msg.id,
      emoji,
    });
  };

  const handleDelete = (msg: Message) => {
    if (confirm('Delete this message?')) {
      sendRaw(channelId, { type: 'message.delete', message_id: msg.id });
    }
  };

  return (
    <div
      className="flex-1 overflow-y-auto py-2 space-y-0.5"
      onScroll={handleScroll}
    >
      {isFetchingNextPage && (
        <div className="text-center text-xs text-gray-500 py-2">
          Loading older messages…
        </div>
      )}

      {channelMsgs.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
          <p>No messages yet. Start the conversation!</p>
        </div>
      )}

      {channelMsgs.map((msg) => (
        <MessageBubble
          key={msg.id}
          msg={msg}
          isMine={msg.author === user?.id}
          onReact={(emoji) => handleReact(msg, emoji)}
          onEdit={() => onEditMessage?.(msg)}
          onDelete={() => handleDelete(msg)}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
