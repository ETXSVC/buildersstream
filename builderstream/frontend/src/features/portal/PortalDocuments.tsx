import { useQuery } from '@tanstack/react-query';
import { Download, FileText } from 'lucide-react';
import { portalClient } from '@/api/portal';

interface PortalDoc {
  id: string;
  title: string;
  file_name: string;
  file_size: number | null;
  content_type: string | null;
  version: number;
  status: string;
  created_at: string;
  download_url: string | null;
}

async function fetchPortalDocs(): Promise<PortalDoc[]> {
  const { data } = await portalClient.get<{ results: PortalDoc[] }>('/api/v1/portal/documents/');
  return data.results;
}

function fmtSize(bytes: number | null): string {
  if (!bytes) return '';
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`;
  if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(0)} KB`;
  return `${bytes} B`;
}

function extFromMime(mime: string | null): string {
  if (!mime) return 'FILE';
  const map: Record<string, string> = {
    'application/pdf': 'PDF',
    'image/jpeg': 'JPG',
    'image/png': 'PNG',
    'application/msword': 'DOC',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
    'application/vnd.ms-excel': 'XLS',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
    'text/plain': 'TXT',
  };
  return map[mime] ?? mime.split('/').pop()?.toUpperCase().slice(0, 5) ?? 'FILE';
}

export function PortalDocuments() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal', 'documents'],
    queryFn: fetchPortalDocs,
    staleTime: 60_000,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Documents</h1>

      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-7 w-7 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Failed to load documents.
        </div>
      )}

      {data && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          {data.length === 0 ? (
            <div className="p-10 text-center text-slate-400 text-sm">No documents shared yet.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs text-slate-500 uppercase tracking-wide">
                  <th className="px-5 py-3 text-left">Document</th>
                  <th className="px-5 py-3 text-left hidden sm:table-cell">Type</th>
                  <th className="px-5 py-3 text-left hidden md:table-cell">Size</th>
                  <th className="px-5 py-3 text-left hidden md:table-cell">Version</th>
                  <th className="px-5 py-3 text-left hidden sm:table-cell">Date</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <FileText size={15} className="text-slate-400 shrink-0" />
                        <div>
                          <p className="font-medium text-slate-900">{doc.title}</p>
                          <p className="text-xs text-slate-400">{doc.file_name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3 hidden sm:table-cell">
                      <span className="rounded-full bg-slate-100 text-slate-600 text-xs px-2 py-0.5 font-medium">
                        {extFromMime(doc.content_type)}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-500 hidden md:table-cell">
                      {fmtSize(doc.file_size)}
                    </td>
                    <td className="px-5 py-3 text-slate-500 hidden md:table-cell">v{doc.version}</td>
                    <td className="px-5 py-3 text-slate-500 hidden sm:table-cell">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3 text-right">
                      {doc.download_url ? (
                        <a
                          href={doc.download_url}
                          download={doc.file_name}
                          className="inline-flex items-center gap-1.5 text-xs text-amber-600 hover:text-amber-700 font-medium"
                        >
                          <Download size={13} />
                          Download
                        </a>
                      ) : (
                        <span className="text-xs text-slate-300">Unavailable</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
