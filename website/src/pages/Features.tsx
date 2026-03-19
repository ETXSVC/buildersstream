import { modules } from '../data/modules';
import ModuleCard from '../components/features/ModuleCard';

const Features = () => {
  return (
    <div className="bg-[#0D0F1E] min-h-screen">
      {/* Header */}
      <div className="bg-[#0D0F1E] text-white pt-28 pb-16 sm:pb-20 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-flex items-center gap-2 bg-violet-900/40 border border-violet-700/40 text-violet-300 text-xs font-semibold uppercase tracking-widest px-4 py-1.5 rounded-full mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 inline-block" />
            22 Modules
          </span>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-4 sm:mb-6 leading-tight">
            Power Your Entire Business
          </h1>
          <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto">
            BuilderStream is modular by design. Every feature you need — from first lead to final invoice — in one unified platform.
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
          {modules.map((module, index) => (
            <ModuleCard key={module.id} module={module} index={index} />
          ))}
        </div>
      </div>

      {/* Integration Banner */}
      <section className="bg-[#080A15] border-t border-white/5 py-16 sm:py-24 mb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Built-In Integrations</h2>
          <p className="text-slate-400 mb-10 max-w-2xl mx-auto">
            Native connections to the services your business already runs on.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6 mb-12">
            {[
              { name: 'Stripe', note: 'Payments & subscriptions', live: true },
              { name: 'Open Exchange Rates', note: 'Multi-currency conversion', live: true },
              { name: 'Weather API', note: 'Field ops & scheduling', live: true },
              { name: 'SMTP / SES', note: 'Transactional email', live: true },
            ].map((tool) => (
              <div key={tool.name} className="flex flex-col items-center justify-center gap-2 p-5 rounded-xl border border-white/5 bg-white/[0.03]">
                <span className="text-white font-semibold text-sm">{tool.name}</span>
                <span className="text-slate-500 text-xs">{tool.note}</span>
                <span className="text-xs bg-emerald-900/40 text-emerald-400 border border-emerald-700/30 px-2 py-0.5 rounded-full">Live</span>
              </div>
            ))}
          </div>

          <h3 className="text-lg font-semibold text-slate-300 mb-6">Coming Soon</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            {[
              { name: 'QuickBooks Online', note: 'Invoice & expense sync' },
              { name: 'Xero', note: 'Accounting sync' },
              { name: 'Slack', note: 'Team notifications' },
              { name: 'Google Workspace', note: 'Calendar & Drive' },
            ].map((tool) => (
              <div key={tool.name} className="flex flex-col items-center justify-center gap-2 p-5 rounded-xl border border-white/5 bg-white/[0.02]">
                <span className="text-slate-300 font-semibold text-sm">{tool.name}</span>
                <span className="text-slate-500 text-xs">{tool.note}</span>
                <span className="text-xs bg-violet-900/30 text-violet-400 border border-violet-700/30 px-2 py-0.5 rounded-full">Roadmap</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Features;
