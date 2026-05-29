import { useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send } from 'lucide-react';
import { fetchPortalMessages, sendPortalMessage } from '@/api/portal';

export function PortalMessages() {
  const qc = useQueryClient();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');

  const { data: messages = [], isLoading, error } = useQuery({
    queryKey: ['portal', 'messages'],
    queryFn: fetchPortalMessages,
    staleTime: 15_000,
    refetchInterval: 30_000,
  });

  const mutation = useMutation({
    mutationFn: () => sendPortalMessage(subject, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portal', 'messages'] });
      qc.invalidateQueries({ queryKey: ['portal', 'dashboard'] });
      setSubject('');
      setBody('');
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    },
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim()) return;
    mutation.mutate();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Messages</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load messages.
        </div>
      )}

      {/* Thread */}
      <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
        {messages.length === 0 && !isLoading && (
          <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-400 text-sm">
            No messages yet. Send a message below.
          </div>
        )}
        {messages.map((msg) => {
          const isClient = msg.sender_type === 'client';
          return (
            <div key={msg.id} className={`flex ${isClient ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-lg rounded-2xl px-4 py-3 ${
                isClient ? 'bg-blue-500 text-white' : 'bg-white border border-slate-200 text-slate-900'
              }`}>
                <div className={`flex items-center gap-2 mb-1 text-xs ${isClient ? 'text-blue-100' : 'text-slate-500'}`}>
                  <span className="font-medium">{isClient ? 'You' : (msg.sender_name ?? 'Contractor')}</span>
                  <span>·</span>
                  <span>{new Date(msg.created_at).toLocaleString()}</span>
                </div>
                {msg.subject && (
                  <p className={`text-xs font-semibold mb-1 ${isClient ? 'text-blue-100' : 'text-slate-600'}`}>
                    Re: {msg.subject}
                  </p>
                )}
                <p className="text-sm whitespace-pre-wrap">{msg.body}</p>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* Compose */}
      <form onSubmit={submit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-3">
        <h2 className="text-sm font-semibold text-slate-700">Send a Message</h2>
        <input
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Subject (optional)"
          className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <textarea
          required
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Write your message…"
          rows={4}
          className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        />
        {mutation.isError && (
          <p className="text-xs text-red-500">Failed to send. Please try again.</p>
        )}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!body.trim() || mutation.isPending}
            className="flex items-center gap-2 px-5 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl text-sm font-medium disabled:opacity-50"
          >
            <Send size={14} />
            {mutation.isPending ? 'Sending…' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
