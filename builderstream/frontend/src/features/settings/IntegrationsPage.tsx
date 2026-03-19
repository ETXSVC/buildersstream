/**
 * Integration Settings — connect / disconnect / sync QB Online and Slack.
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';

interface AvailableIntegration {
  integration_type: string;
  label: string;
  status: string;
  connection_id: string | null;
  last_sync_at: string | null;
}


const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  connected: { label: 'Connected', color: 'text-green-700 bg-green-50 border-green-200' },
  disconnected: { label: 'Disconnected', color: 'text-slate-600 bg-slate-50 border-slate-200' },
  error: { label: 'Error', color: 'text-red-700 bg-red-50 border-red-200' },
  syncing: { label: 'Syncing', color: 'text-blue-700 bg-blue-50 border-blue-200' },
  not_configured: { label: 'Not configured', color: 'text-slate-400 bg-white border-slate-200' },
};

const INTEGRATION_ICONS: Record<string, string> = {
  quickbooks_online: '📊',
  slack: '💬',
  xero: '📋',
  google_workspace: '🔵',
};

function useAvailableIntegrations() {
  return useQuery<AvailableIntegration[]>({
    queryKey: ['integrations', 'available'],
    queryFn: async () => {
      const { data } = await apiClient.get<AvailableIntegration[]>(
        '/api/v1/integrations/connections/available/'
      );
      return data;
    },
  });
}

function SlackConfigForm({ connectionId, onSaved }: { connectionId: string | null; onSaved: () => void }) {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!webhookUrl.startsWith('https://hooks.slack.com/')) {
      setError('Enter a valid Slack Incoming Webhook URL.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      if (connectionId) {
        await apiClient.patch(`/api/v1/integrations/connections/${connectionId}/`, {
          sync_config: { webhook_url: webhookUrl },
          status: 'connected',
        });
      } else {
        await apiClient.post('/api/v1/integrations/connections/', {
          integration_type: 'slack',
          sync_config: { webhook_url: webhookUrl },
          status: 'connected',
        });
      }
      setWebhookUrl('');
      onSaved();
    } catch {
      setError('Failed to save. Check the webhook URL and try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-3 space-y-2">
      <label className="block text-xs font-medium text-slate-600">Slack Incoming Webhook URL</label>
      <input
        type="url"
        value={webhookUrl}
        onChange={(e) => setWebhookUrl(e.target.value)}
        placeholder="https://hooks.slack.com/services/..."
        className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
      <p className="text-xs text-slate-400">
        Create a webhook at{' '}
        <span className="font-mono">api.slack.com/apps → Incoming Webhooks</span>.
        Channels used: <span className="font-mono">#projects</span>, <span className="font-mono">#crm</span>,{' '}
        <span className="font-mono">#finance</span>, <span className="font-mono">#safety</span>.
      </p>
      <button
        type="button"
        onClick={handleSave}
        disabled={saving}
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
      >
        {saving ? 'Saving…' : 'Save Webhook'}
      </button>
    </div>
  );
}

function IntegrationCard({ integration }: { integration: AvailableIntegration }) {
  const queryClient = useQueryClient();
  const [showSlackForm, setShowSlackForm] = useState(false);
  const statusMeta = STATUS_LABELS[integration.status] ?? STATUS_LABELS.not_configured;
  const icon = INTEGRATION_ICONS[integration.integration_type] ?? '🔌';
  const isConnected = integration.status === 'connected';

  const connectMutation = useMutation({
    mutationFn: async () => {
      if (!integration.connection_id) throw new Error('No connection ID');
      const { data } = await apiClient.post<{ authorization_url?: string }>(
        `/api/v1/integrations/connections/${integration.connection_id}/connect/`
      );
      if (data.authorization_url) window.location.href = data.authorization_url;
    },
  });

  const disconnectMutation = useMutation({
    mutationFn: async () => {
      if (!integration.connection_id) return;
      await apiClient.post(`/api/v1/integrations/connections/${integration.connection_id}/disconnect/`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['integrations', 'available'] }),
  });

  const syncMutation = useMutation({
    mutationFn: async () => {
      if (!integration.connection_id) return;
      await apiClient.post(`/api/v1/integrations/connections/${integration.connection_id}/sync/`);
    },
  });

  const isSlack = integration.integration_type === 'slack';
  const isQB = integration.integration_type === 'quickbooks_online';

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <p className="font-medium text-slate-900">{integration.label}</p>
            {integration.last_sync_at && (
              <p className="text-xs text-slate-400 mt-0.5">
                Last sync: {new Date(integration.last_sync_at).toLocaleString()}
              </p>
            )}
          </div>
        </div>
        <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium ${statusMeta.color}`}>
          {statusMeta.label}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {isSlack && !isConnected && (
          <button
            type="button"
            onClick={() => setShowSlackForm((v) => !v)}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            {showSlackForm ? 'Cancel' : 'Configure Webhook'}
          </button>
        )}

        {isQB && !isConnected && integration.connection_id && (
          <button
            type="button"
            onClick={() => connectMutation.mutate()}
            disabled={connectMutation.isPending}
            className="rounded-lg bg-green-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-600 disabled:opacity-50"
          >
            {connectMutation.isPending ? 'Redirecting…' : 'Connect QuickBooks'}
          </button>
        )}

        {isConnected && (
          <>
            {!isSlack && (
              <button
                type="button"
                onClick={() => syncMutation.mutate()}
                disabled={syncMutation.isPending}
                className="rounded-lg bg-blue-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
              >
                {syncMutation.isPending ? 'Syncing…' : 'Sync Now'}
              </button>
            )}
            <button
              type="button"
              onClick={() => disconnectMutation.mutate()}
              disabled={disconnectMutation.isPending}
              className="rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
            >
              {disconnectMutation.isPending ? 'Disconnecting…' : 'Disconnect'}
            </button>
          </>
        )}
      </div>

      {isSlack && showSlackForm && (
        <SlackConfigForm
          connectionId={integration.connection_id}
          onSaved={() => {
            setShowSlackForm(false);
            queryClient.invalidateQueries({ queryKey: ['integrations', 'available'] });
          }}
        />
      )}
    </div>
  );
}

export const IntegrationsPage = () => {
  const { data: integrations, isLoading, error } = useAvailableIntegrations();

  // Only show QB and Slack prominently; others in a "coming soon" section
  const primary = integrations?.filter((i) =>
    ['quickbooks_online', 'slack'].includes(i.integration_type)
  ) ?? [];
  const coming = integrations?.filter((i) =>
    !['quickbooks_online', 'slack'].includes(i.integration_type)
  ) ?? [];

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Integrations</h1>
        <p className="mt-1 text-sm text-slate-500">
          Connect external services to sync data and receive notifications.
        </p>
      </div>

      {isLoading && (
        <div className="flex h-32 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load integrations.
        </div>
      )}

      {primary.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-700">Available</h2>
          {primary.map((i) => (
            <IntegrationCard key={i.integration_type} integration={i} />
          ))}
        </section>
      )}

      {coming.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-700">Coming Soon</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {coming.map((i) => (
              <div
                key={i.integration_type}
                className="flex items-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 opacity-60"
              >
                <span className="text-xl">{INTEGRATION_ICONS[i.integration_type] ?? '🔌'}</span>
                <div>
                  <p className="text-sm font-medium text-slate-700">{i.label}</p>
                  <p className="text-xs text-slate-400">In development</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
