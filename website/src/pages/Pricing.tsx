import React from 'react';
import { Check } from 'lucide-react';

const Pricing = () => {
  const tiers = [
    {
      name: 'Starter',
      price: 'TBD',
      audience: 'For Solo Remodelers',
      features: ['Project Command Center', 'CRM (Up to 50 leads)', 'Basic Estimating', 'Mobile App Access', '5 Active Projects'],
      cta: 'Coming Soon',
      primary: false
    },
    {
      name: 'Professional',
      price: 'TBD',
      audience: 'For Growing GCs',
      features: ['Everything in Starter', 'Unlimited CRM', 'Advanced Scheduling', 'Financial Management', 'Client Portal', 'Unlimited Projects'],
      cta: 'Coming Soon',
      primary: true
    },
    {
      name: 'Enterprise',
      price: 'TBD',
      audience: 'For Large Firms',
      features: ['Everything in Professional', 'API Access', 'Dedicated Success Manager', 'SSO & Advanced Security', 'Custom Reporting'],
      cta: 'Coming Soon',
      primary: false
    }
  ];

  return (
    <div className="bg-neutral-light min-h-screen pt-24 pb-12 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center mb-12 sm:mb-16">
        <h1 className="text-3xl sm:text-4xl font-bold text-neutral-slate mb-4">Transparent Pricing</h1>
        <p className="text-lg sm:text-xl text-neutral-gray text-neutral-500">No hidden fees. Cancel anytime.</p>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6 lg:gap-8">
        {tiers.map((tier) => (
            <div key={tier.name} className={`relative flex flex-col p-6 sm:p-8 rounded-2xl border ${tier.primary ? 'border-primary shadow-2xl md:scale-105 z-10 bg-[#1e293b]' : 'border-neutral-800 bg-[#1e293b] shadow-sm hover:shadow-lg transition-shadow'}`}>
                {tier.primary && (
                    <div className="absolute top-0 right-0 left-0 -mt-4 flex justify-center">
                        <span className="bg-primary text-white text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full">Most Popular</span>
                    </div>
                )}
                <h3 className="text-2xl font-bold text-neutral-slate">{tier.name}</h3>
                <p className="text-sm text-neutral-500 mb-6">{tier.audience}</p>
                <div className="text-4xl sm:text-5xl font-bold text-neutral-slate mb-6">{tier.price}<span className="text-lg font-medium text-neutral-400">/mo</span></div>
                
                <button className={`w-full py-4 rounded-xl font-semibold mb-8 transition-colors ${tier.primary ? 'bg-secondary hover:bg-secondary-hover text-white' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-slate'}`}>
                    {tier.cta}
                </button>

                <ul className="space-y-4 flex-grow">
                    {tier.features.map((feature) => (
                        <li key={feature} className="flex items-start space-x-3 text-sm text-neutral-400">
                             <Check className="h-5 w-5 text-primary flex-shrink-0" />
                             <span>{feature}</span>
                        </li>
                    ))}
                </ul>
            </div>
        ))}
      </div>
    </div>
  );
};

export default Pricing;
