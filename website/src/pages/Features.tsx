import React from 'react';
import { modules } from '../data/modules';
import ModuleCard from '../components/features/ModuleCard';

const Features = () => {
  return (
    <div className="bg-neutral-light min-h-screen">
      {/* Header */}
      <div className="bg-[#020617] text-white pt-24 pb-24 sm:pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6">Power Your Entire Business</h1>
          <p className="text-base sm:text-lg md:text-xl text-neutral-300 max-w-3xl mx-auto">
            Builders Stream Pro is modular by design. Start with what you need and scale up as you grow.
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12 sm:-mt-20 pb-16 sm:pb-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          {modules.map((module, index) => (
            <ModuleCard key={module.id} module={module} index={index} />
          ))}
        </div>
      </div>

      {/* Integration Banner */}
      <section className="bg-[#0f172a] py-16 sm:py-24 mb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-neutral-slate mb-8 sm:mb-12">Integrates With Your Favorite Tools</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-6">
                {['QuickBooks', 'Gmail', 'Outlook', 'Slack', 'Zoom', 'Dropbox'].map((tool) => (
                     <div key={tool} className="flex items-center justify-center p-4 sm:p-6 border border-neutral-100 rounded-xl bg-neutral-50 text-neutral-400 font-bold text-base sm:text-xl">
                        {tool}
                     </div>
                ))}
            </div>
        </div>
      </section>
    </div>
  );
};

export default Features;
