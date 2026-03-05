import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useKanbanBoard, useKanbanMove } from '@/hooks/useKanban';
import type { KanbanProject, KanbanColumn } from '@/api/kanban';

const HEALTH_DOT: Record<string, string> = {
  green: 'bg-green-500',
  yellow: 'bg-yellow-400',
  red: 'bg-red-500',
};

const COLUMN_HEADER: Record<string, string> = {
  blue: 'border-blue-400 bg-blue-50',
  purple: 'border-purple-400 bg-purple-50',
  indigo: 'border-indigo-400 bg-indigo-50',
  cyan: 'border-cyan-400 bg-cyan-50',
  amber: 'border-amber-400 bg-amber-50',
  orange: 'border-orange-400 bg-orange-50',
  teal: 'border-teal-400 bg-teal-50',
  lime: 'border-lime-400 bg-lime-50',
  green: 'border-green-400 bg-green-50',
  red: 'border-red-400 bg-red-50',
};

export const KanbanPage = () => {
  const [showAll, setShowAll] = useState(false);
  const { data, isLoading, error } = useKanbanBoard(showAll);
  const move = useKanbanMove();

  const dragProject = useRef<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);
  const [moveError, setMoveError] = useState('');

  const handleDragStart = (projectId: string) => {
    dragProject.current = projectId;
  };

  const handleDrop = (targetStatus: string) => {
    setDragOver(null);
    const id = dragProject.current;
    if (!id) return;
    dragProject.current = null;
    setMoveError('');
    move.mutate(
      { id, new_status: targetStatus },
      {
        onError: (err: unknown) => {
          const msg =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            ?? 'Cannot move project to that status.';
          setMoveError(msg);
        },
      },
    );
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 text-sm text-red-600">Failed to load kanban board.</div>
    );
  }

  return (
    <div className="flex h-full flex-col p-6">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Kanban Board</h1>
        <div className="flex items-center gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={showAll}
              onChange={(e) => setShowAll(e.target.checked)}
              className="rounded"
            />
            Show completed / canceled
          </label>
          <Link
            to="/projects"
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            List View
          </Link>
        </div>
      </div>

      {moveError && (
        <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {moveError}
        </div>
      )}

      {/* Board */}
      <div className="flex flex-1 gap-3 overflow-x-auto pb-4">
        {data.columns.map((col) => (
          <KanbanColumn
            key={col.status}
            column={col}
            isDragOver={dragOver === col.status}
            onDragOver={(e) => { e.preventDefault(); setDragOver(col.status); }}
            onDragLeave={() => setDragOver(null)}
            onDrop={() => handleDrop(col.status)}
            onCardDragStart={handleDragStart}
          />
        ))}
      </div>
    </div>
  );
};

// -----------------------------------------------------------------------

interface KanbanColumnProps {
  column: KanbanColumn;
  isDragOver: boolean;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: () => void;
  onCardDragStart: (id: string) => void;
}

function KanbanColumn({ column, isDragOver, onDragOver, onDragLeave, onDrop, onCardDragStart }: KanbanColumnProps) {
  const headerClass = COLUMN_HEADER[column.color] ?? 'border-slate-300 bg-slate-50';

  return (
    <div
      className={[
        'flex w-64 flex-shrink-0 flex-col rounded-xl border-2 transition-colors',
        isDragOver ? 'border-amber-400 bg-amber-50/40' : 'border-slate-200 bg-slate-50',
      ].join(' ')}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {/* Column header */}
      <div className={`rounded-t-xl border-b-2 px-3 py-2 ${headerClass}`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-700">
            {column.label}
          </span>
          <span className="rounded-full bg-white px-2 py-0.5 text-xs font-bold text-slate-600 shadow-sm">
            {column.count}
          </span>
        </div>
      </div>

      {/* Cards */}
      <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-2">
        {column.projects.length === 0 && (
          <p className="py-6 text-center text-xs text-slate-400">No projects</p>
        )}
        {column.projects.map((project) => (
          <KanbanCard
            key={project.id}
            project={project}
            onDragStart={() => onCardDragStart(project.id)}
          />
        ))}
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------

interface KanbanCardProps {
  project: KanbanProject;
  onDragStart: () => void;
}

function KanbanCard({ project, onDragStart }: KanbanCardProps) {
  return (
    <div
      draggable
      onDragStart={onDragStart}
      className="cursor-grab rounded-lg border border-slate-200 bg-white p-3 shadow-sm transition hover:shadow-md active:cursor-grabbing"
    >
      <div className="mb-1 flex items-start justify-between gap-1">
        <Link
          to={`/projects/${project.id}`}
          className="text-sm font-medium text-slate-900 hover:text-amber-700 line-clamp-2"
          draggable={false}
        >
          {project.name}
        </Link>
        {project.health_status && (
          <span className={`mt-1 h-2.5 w-2.5 flex-shrink-0 rounded-full ${HEALTH_DOT[project.health_status]}`} />
        )}
      </div>

      <p className="mb-2 text-xs text-slate-400">{project.project_number}</p>

      {project.client_name && (
        <p className="text-xs text-slate-500 truncate">{project.client_name}</p>
      )}

      {project.estimated_value && (
        <p className="mt-1 text-xs font-semibold text-slate-700">
          ${Number(project.estimated_value).toLocaleString()}
        </p>
      )}

      {project.estimated_completion && (
        <p className="mt-1 text-xs text-slate-400">
          Due {new Date(project.estimated_completion).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
