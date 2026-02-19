import { useState } from 'react';
import { useDocuments, useRFIs, useSubmittals, usePhotos } from '@/hooks/useDocuments';
import { RFI_STATUS_COLORS, SUBMITTAL_STATUS_COLORS } from '@/types/documents';

type Tab = 'documents' | 'rfis' | 'submittals' | 'photos';

export const DocumentsPage = () => {
  const [tab, setTab] = useState<Tab>('documents');
  const [search, setSearch] = useState('');

  const tabs: { key: Tab; label: string }[] = [
    { key: 'documents', label: 'Documents' },
    { key: 'rfis', label: 'RFIs' },
    { key: 'submittals', label: 'Submittals' },
    { key: 'photos', label: 'Photos' },
  ];

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
      </div>

      <div className="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={[
              'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
              tab === t.key ? 'bg-amber-500 text-white' : 'text-slate-600 hover:text-slate-900',
            ].join(' ')}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mb-4">
        <input
          type="search"
          placeholder={`Search ${tab}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-xs rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
        />
      </div>

      {tab === 'documents' && <DocumentsTable search={search} />}
      {tab === 'rfis' && <RFIsTable search={search} />}
      {tab === 'submittals' && <SubmittalsTable search={search} />}
      {tab === 'photos' && <PhotosGrid search={search} />}
    </div>
  );
};

function DocumentsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20', is_current_version: 'true' };
  if (search) params.search = search;
  const { data, isLoading } = useDocuments(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>Title</Th>
            <Th>Project</Th>
            <Th>Folder</Th>
            <Th>Type</Th>
            <Th>Version</Th>
            <Th>Uploaded By</Th>
            <Th>Date</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No documents found.</td></tr>
          )}
          {data?.results.map((doc) => (
            <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileIcon type={doc.file_type} />
                  {doc.download_url ? (
                    <a
                      href={doc.download_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-amber-600 hover:underline"
                    >
                      {doc.title}
                    </a>
                  ) : (
                    <span className="font-medium text-slate-900">{doc.title}</span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-slate-500 text-xs">{doc.project_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{doc.folder_name ?? '—'}</td>
              <td className="px-4 py-3">
                {doc.file_type && (
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs uppercase text-slate-600">
                    {doc.file_type}
                  </span>
                )}
              </td>
              <td className="px-4 py-3 text-center text-slate-500">v{doc.version_number}</td>
              <td className="px-4 py-3 text-slate-600">{doc.uploaded_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-500">
                {new Date(doc.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="documents" />
    </div>
  );
}

function RFIsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useRFIs(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>RFI #</Th>
            <Th>Project</Th>
            <Th>Title</Th>
            <Th>Submitted By</Th>
            <Th>Due Date</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No RFIs found.</td></tr>
          )}
          {data?.results.map((rfi) => (
            <tr key={rfi.id} className={`hover:bg-slate-50 transition-colors ${rfi.is_overdue ? 'bg-red-50/40' : ''}`}>
              <td className="px-4 py-3 font-medium text-slate-900">RFI-{String(rfi.rfi_number).padStart(3, '0')}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{rfi.project_name}</td>
              <td className="px-4 py-3 text-slate-900">
                {rfi.title}
                {rfi.is_overdue && (
                  <span className="ml-2 rounded-full bg-red-100 px-1.5 py-0.5 text-xs text-red-600">Overdue</span>
                )}
              </td>
              <td className="px-4 py-3 text-slate-600">{rfi.submitted_by_name ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {rfi.due_date ? new Date(rfi.due_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${RFI_STATUS_COLORS[rfi.status]}`}>
                  {rfi.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="RFIs" />
    </div>
  );
}

function SubmittalsTable({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '20' };
  if (search) params.search = search;
  const { data, isLoading } = useSubmittals(params);

  if (isLoading) return <Spinner />;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <Th>#</Th>
            <Th>Project</Th>
            <Th>Title</Th>
            <Th>Spec Section</Th>
            <Th>Submitted</Th>
            <Th>Required By</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {data?.results.length === 0 && (
            <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-400">No submittals found.</td></tr>
          )}
          {data?.results.map((sub) => (
            <tr key={sub.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">{String(sub.submittal_number).padStart(3, '0')}</td>
              <td className="px-4 py-3 text-slate-500 text-xs">{sub.project_name}</td>
              <td className="px-4 py-3 text-slate-900">{sub.title}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-500">{sub.spec_section ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {sub.submitted_date ? new Date(sub.submitted_date).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {sub.required_by ? new Date(sub.required_by).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SUBMITTAL_STATUS_COLORS[sub.status]}`}>
                  {sub.status.replace(/_/g, ' ')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination count={data?.count} shown={data?.results.length} label="submittals" />
    </div>
  );
}

function PhotosGrid({ search }: { search: string }) {
  const params: Record<string, string> = { page_size: '24' };
  if (search) params.search = search;
  const { data, isLoading } = usePhotos(params);

  if (isLoading) return <Spinner />;
  return (
    <div>
      {data?.results.length === 0 && (
        <div className="flex h-40 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 text-sm">
          No photos found.
        </div>
      )}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {data?.results.map((photo) => (
          <a
            key={photo.id}
            href={photo.download_url ?? '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="group relative aspect-square overflow-hidden rounded-xl border border-slate-200 bg-slate-100"
          >
            {photo.thumbnail_url ? (
              <img
                src={photo.thumbnail_url}
                alt={photo.caption ?? 'Site photo'}
                className="h-full w-full object-cover transition-transform group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-slate-300">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
            )}
            {photo.caption && (
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                <p className="text-xs text-white line-clamp-2">{photo.caption}</p>
              </div>
            )}
          </a>
        ))}
      </div>
      <Pagination count={data?.count} shown={data?.results.length} label="photos" />
    </div>
  );
}

function FileIcon({ type }: { type: string | null }) {
  const colors: Record<string, string> = {
    pdf: 'text-red-500', xlsx: 'text-green-600', xls: 'text-green-600',
    docx: 'text-blue-600', doc: 'text-blue-600', jpg: 'text-amber-500',
    jpeg: 'text-amber-500', png: 'text-amber-500',
  };
  const color = type ? (colors[type.toLowerCase()] ?? 'text-slate-400') : 'text-slate-400';
  return (
    <svg className={`h-4 w-4 flex-shrink-0 ${color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
      {children}
    </th>
  );
}

function Spinner() {
  return (
    <div className="flex h-40 items-center justify-center">
      <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
    </div>
  );
}

function Pagination({ count, shown, label }: { count?: number; shown?: number; label: string }) {
  if (!count || !shown || count <= shown) return null;
  return (
    <div className="border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
      Showing {shown} of {count} {label}
    </div>
  );
}
