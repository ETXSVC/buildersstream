import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import React from 'react';

interface ModuleProps {
  module: {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    benefits: string[];
    badge?: string;
  };
  index: number;
}

const ModuleCard = ({ module, index }: ModuleProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: Math.min(index * 0.04, 0.4) }}
      className="flex flex-col bg-white/[0.03] rounded-2xl border border-white/5 p-8 hover:shadow-xl hover:shadow-violet-900/10 transition-all duration-300 hover:border-violet-500/20 group"
    >
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-violet-600/15 rounded-xl border border-violet-500/20 group-hover:bg-violet-600/25 transition-colors">
            <module.icon className="h-6 w-6 text-violet-400" />
          </div>
          <h3 className="text-lg font-bold text-white">{module.title}</h3>
        </div>
        {module.badge && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border flex-shrink-0 ml-2 ${
            module.badge === 'Enterprise'
              ? 'bg-amber-900/30 text-amber-400 border-amber-700/30'
              : 'bg-violet-900/40 text-violet-300 border-violet-700/30'
          }`}>
            {module.badge}
          </span>
        )}
      </div>

      <p className="text-slate-400 mb-6 flex-grow leading-relaxed text-sm">
        {module.description}
      </p>

      <ul className="space-y-2.5">
        {module.benefits.map((benefit, i) => (
          <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
            <Check className="h-4 w-4 text-violet-400 flex-shrink-0 mt-0.5" />
            <span>{benefit}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
};

export default ModuleCard;
