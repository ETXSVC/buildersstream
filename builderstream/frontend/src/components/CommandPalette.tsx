import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { universalSearch } from '@/api/search';
import type { SearchResult } from '@/api/search';

const TYPE_ICONS: Record<SearchResult['type'], string> = {
  project: '🏗️',
  contact: '👤',
  lead: '📋',
  estimate: '💰',
  invoice: '🧾',
  document: '📄',
};

const TYPE_LABELS: Record<SearchResult['type'], string> = {
  project: 'Project',
  contact: 'Contact',
  lead: 'Lead',
  estimate: 'Estimate',
  invoice: 'Invoice',
  document: 'Document',
};

export const CommandPalette = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Keyboard shortcut: Cmd+K / Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  useEffect(() => {
    if (open) {
      setQuery('');
      setResults([]);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  const search = useCallback((q: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (q.length < 2) { setResults([]); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await universalSearch(q);
        setResults(res.results);
        setActiveIdx(0);
      } finally {
        setLoading(false);
      }
    }, 200);
  }, []);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActiveIdx((i) => Math.min(i + 1, results.length - 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActiveIdx((i) => Math.max(i - 1, 0)); }
    if (e.key === 'Enter' && results[activeIdx]) {
      navigate(results[activeIdx].url);
      setOpen(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24" onClick={() => setOpen(false)}>
      <div
        className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-slate-100 px-4 py-3">
          <svg className="h-4 w-4 flex-shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); search(e.target.value); }}
            onKeyDown={handleKey}
            placeholder="Search projects, contacts, estimates…"
            className="flex-1 bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
          />
          {loading && <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />}
          <kbd className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-400">ESC</kbd>
        </div>

        {/* Results */}
        {results.length > 0 ? (
          <div className="max-h-80 overflow-y-auto py-2">
            {results.map((r, i) => (
              <button
                key={r.id + r.type}
                type="button"
                className={[
                  'flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors',
                  i === activeIdx ? 'bg-blue-50' : 'hover:bg-slate-50',
                ].join(' ')}
                onClick={() => { navigate(r.url); setOpen(false); }}
              >
                <span className="text-base">{TYPE_ICONS[r.type]}</span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-900">{r.title}</p>
                  <p className="truncate text-xs text-slate-500">{r.subtitle}</p>
                </div>
                <span className="flex-shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">
                  {TYPE_LABELS[r.type]}
                </span>
              </button>
            ))}
          </div>
        ) : query.length >= 2 && !loading ? (
          <div className="py-8 text-center text-sm text-slate-400">No results found for "{query}"</div>
        ) : query.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-400">
            Type to search across projects, contacts, estimates, and more
          </div>
        ) : null}

        <div className="border-t border-slate-100 px-4 py-2 flex gap-4 text-[10px] text-slate-400">
          <span><kbd className="rounded bg-slate-100 px-1">↑↓</kbd> navigate</span>
          <span><kbd className="rounded bg-slate-100 px-1">↵</kbd> open</span>
          <span><kbd className="rounded bg-slate-100 px-1">⌘K</kbd> toggle</span>
        </div>
      </div>
    </div>
  );
};
