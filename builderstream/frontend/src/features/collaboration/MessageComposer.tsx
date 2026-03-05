import { useEffect, useRef, useState } from 'react';
import { Send, X } from 'lucide-react';
import { useChatStore } from '@/stores/chat';
import type { Message } from '@/api/collaboration';

interface Props {
  channelId: string;
  editingMessage?: Message | null;
  onCancelEdit?: () => void;
}

export function MessageComposer({ channelId, editingMessage, onCancelEdit }: Props) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { sendRaw } = useChatStore();

  // Populate textarea when editing
  useEffect(() => {
    if (editingMessage) {
      setText(editingMessage.content);
      textareaRef.current?.focus();
    } else {
      setText('');
    }
  }, [editingMessage]);

  const handleSend = () => {
    const content = text.trim();
    if (!content) return;

    if (editingMessage) {
      sendRaw(channelId, {
        type: 'message.edit',
        message_id: editingMessage.id,
        content,
      });
      onCancelEdit?.();
    } else {
      sendRaw(channelId, { type: 'message.send', content });
    }
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === 'Escape' && editingMessage) {
      onCancelEdit?.();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [text]);

  // Broadcast typing event (debounced)
  const typingTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    if (typingTimeout.current) clearTimeout(typingTimeout.current);
    sendRaw(channelId, { type: 'typing' });
    typingTimeout.current = setTimeout(() => {
      typingTimeout.current = null;
    }, 2000);
  };

  return (
    <div className="px-4 pb-4">
      {editingMessage && (
        <div className="flex items-center gap-2 mb-1 text-xs text-amber-400">
          <span>Editing message</span>
          <button
            type="button"
            onClick={onCancelEdit}
            className="hover:text-white"
            title="Cancel edit"
          >
            <X size={12} />
          </button>
        </div>
      )}
      <div className="flex items-end gap-2 bg-gray-700 rounded-lg px-3 py-2">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send, Shift+Enter for new line)"
          rows={1}
          className="flex-1 bg-transparent text-sm text-gray-200 placeholder-gray-500 resize-none outline-none max-h-40"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!text.trim()}
          className="text-indigo-400 hover:text-indigo-300 disabled:opacity-30 disabled:cursor-not-allowed shrink-0 mb-0.5"
          title="Send"
        >
          <Send size={18} />
        </button>
      </div>
      <p className="text-xs text-gray-600 mt-1">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
