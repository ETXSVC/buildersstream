import { useState } from 'react';
import { useComments, useCreateComment, useUpdateComment, useDeleteComment } from '@/hooks/useComments';
import { useAuth } from '@/hooks/useAuth';
import type { Comment } from '@/api/comments';

interface Props {
  projectId: string;
}

export const ProjectComments = ({ projectId }: Props) => {
  const { data: comments = [], isLoading } = useComments(projectId);
  const create = useCreateComment(projectId);
  const [body, setBody] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim()) return;
    create.mutate({ body: body.trim() }, { onSuccess: () => setBody('') });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-700">Comments</h3>

      {isLoading ? (
        <div className="flex h-16 items-center justify-center">
          <div className="h-5 w-5 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      ) : comments.length === 0 ? (
        <p className="text-sm text-slate-400">No comments yet. Be the first to add one.</p>
      ) : (
        <div className="space-y-3">
          {comments.map((c) => (
            <CommentThread key={c.id} comment={c} projectId={projectId} />
          ))}
        </div>
      )}

      {/* New top-level comment */}
      <form onSubmit={handleSubmit} className="flex gap-2 pt-2">
        <textarea
          rows={2}
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Write a comment…"
          className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-amber-400 focus:outline-none resize-none"
        />
        <button
          type="submit"
          disabled={create.isPending || !body.trim()}
          className="self-end rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
        >
          Post
        </button>
      </form>
    </div>
  );
};

/* ---------- Single comment + replies ---------- */

function CommentThread({ comment, projectId }: { comment: Comment; projectId: string }) {
  const { user } = useAuth();
  const update = useUpdateComment(projectId);
  const remove = useDeleteComment(projectId);
  const reply = useCreateComment(projectId);

  const [editing, setEditing] = useState(false);
  const [editBody, setEditBody] = useState(comment.body);
  const [replying, setReplying] = useState(false);
  const [replyBody, setReplyBody] = useState('');

  const isAuthor = user && comment.author === (user as { id?: string }).id;

  const handleEdit = (e: React.FormEvent) => {
    e.preventDefault();
    update.mutate({ id: comment.id, body: editBody }, { onSuccess: () => setEditing(false) });
  };

  const handleReply = (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyBody.trim()) return;
    reply.mutate(
      { body: replyBody.trim(), parent: comment.id },
      { onSuccess: () => { setReplying(false); setReplyBody(''); } }
    );
  };

  return (
    <div className="rounded-lg border border-slate-100 bg-white p-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-[10px] font-bold text-amber-700">
            {comment.author_name?.[0]?.toUpperCase() ?? '?'}
          </div>
          <span className="text-xs font-medium text-slate-700">{comment.author_name}</span>
          {comment.is_edited && <span className="text-[10px] text-slate-400">(edited)</span>}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-400">{new Date(comment.created_at).toLocaleString()}</span>
          {isAuthor && !comment.is_deleted && (
            <>
              <button type="button" onClick={() => setEditing(true)}
                className="text-[10px] text-slate-400 hover:text-slate-600">Edit</button>
              <button type="button" onClick={() => remove.mutate(comment.id)}
                className="text-[10px] text-red-400 hover:text-red-600">Delete</button>
            </>
          )}
        </div>
      </div>

      {/* Body */}
      {editing ? (
        <form onSubmit={handleEdit} className="flex gap-2">
          <textarea
            rows={2}
            value={editBody}
            onChange={(e) => setEditBody(e.target.value)}
            className="flex-1 rounded border border-slate-200 px-2 py-1 text-sm focus:border-amber-400 focus:outline-none resize-none"
          />
          <div className="flex flex-col gap-1">
            <button type="submit" className="rounded bg-amber-500 px-2 py-1 text-xs text-white hover:bg-amber-600">Save</button>
            <button type="button" onClick={() => setEditing(false)} className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600 hover:bg-slate-200">Cancel</button>
          </div>
        </form>
      ) : (
        <p className={`text-sm ${comment.is_deleted ? 'italic text-slate-400' : 'text-slate-700'}`}>
          {comment.body}
        </p>
      )}

      {/* Reply button */}
      {!comment.is_deleted && !replying && (
        <button type="button" onClick={() => setReplying(true)}
          className="mt-1.5 text-[10px] text-amber-600 hover:underline">
          Reply
        </button>
      )}

      {/* Reply form */}
      {replying && (
        <form onSubmit={handleReply} className="mt-2 flex gap-2">
          <textarea
            rows={2}
            value={replyBody}
            onChange={(e) => setReplyBody(e.target.value)}
            placeholder="Write a reply…"
            className="flex-1 rounded border border-slate-200 px-2 py-1 text-sm focus:border-amber-400 focus:outline-none resize-none"
          />
          <div className="flex flex-col gap-1">
            <button type="submit" disabled={!replyBody.trim()} className="rounded bg-amber-500 px-2 py-1 text-xs text-white hover:bg-amber-600 disabled:opacity-50">Reply</button>
            <button type="button" onClick={() => setReplying(false)} className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">Cancel</button>
          </div>
        </form>
      )}

      {/* Replies */}
      {comment.replies.length > 0 && (
        <div className="mt-3 space-y-2 border-l-2 border-amber-100 pl-3">
          {comment.replies.map((r) => (
            <ReplyItem key={r.id} reply={r} projectId={projectId} />
          ))}
        </div>
      )}
    </div>
  );
}

function ReplyItem({ reply, projectId }: { reply: Comment; projectId: string }) {
  const { user } = useAuth();
  const update = useUpdateComment(projectId);
  const remove = useDeleteComment(projectId);
  const [editing, setEditing] = useState(false);
  const [editBody, setEditBody] = useState(reply.body);
  const isAuthor = user && reply.author === (user as { id?: string }).id;

  return (
    <div>
      <div className="flex items-center gap-2 mb-0.5">
        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-100 text-[9px] font-bold text-slate-500">
          {reply.author_name?.[0]?.toUpperCase() ?? '?'}
        </div>
        <span className="text-xs font-medium text-slate-600">{reply.author_name}</span>
        <span className="text-[10px] text-slate-400">{new Date(reply.created_at).toLocaleString()}</span>
        {isAuthor && !reply.is_deleted && (
          <>
            <button type="button" onClick={() => setEditing(true)} className="text-[10px] text-slate-400 hover:text-slate-600">Edit</button>
            <button type="button" onClick={() => remove.mutate(reply.id)} className="text-[10px] text-red-400 hover:text-red-600">Delete</button>
          </>
        )}
      </div>
      {editing ? (
        <form onSubmit={(e) => { e.preventDefault(); update.mutate({ id: reply.id, body: editBody }, { onSuccess: () => setEditing(false) }); }} className="flex gap-1.5 mt-1">
          <textarea rows={2} value={editBody} onChange={(e) => setEditBody(e.target.value)}
            className="flex-1 rounded border border-slate-200 px-2 py-1 text-xs resize-none focus:outline-none focus:border-amber-400" />
          <div className="flex flex-col gap-1">
            <button type="submit" className="rounded bg-amber-500 px-2 py-0.5 text-[10px] text-white">Save</button>
            <button type="button" onClick={() => setEditing(false)} className="rounded bg-slate-100 px-2 py-0.5 text-[10px] text-slate-600">Cancel</button>
          </div>
        </form>
      ) : (
        <p className={`text-xs ${reply.is_deleted ? 'italic text-slate-400' : 'text-slate-600'}`}>{reply.body}</p>
      )}
    </div>
  );
}
