import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

interface ModuleProps {
  module: {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    benefits: string[];
  };
  index: number;
}

const ModuleCard = ({ module, index }: ModuleProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.05 }}
      className="flex flex-col bg-[#1e293b] rounded-2xl border border-neutral-800 p-8 hover:shadow-xl transition-all duration-300 hover:border-primary/20 group"
    >
      <div className="flex items-center space-x-4 mb-6">
        <div className="p-3 bg-[#0f172a] rounded-xl group-hover:bg-primary/10 transition-colors">
          <module.icon className="h-8 w-8 text-neutral-slate group-hover:text-primary transition-colors" />
        </div>
        <h3 className="text-xl font-bold text-neutral-slate">{module.title}</h3>
      </div>
      
      <p className="text-neutral-gray mb-8 flex-grow leading-relaxed">
        {module.description}
      </p>

      <ul className="space-y-3">
        {module.benefits.map((benefit, i) => (
          <li key={i} className="flex items-start space-x-3 text-sm text-neutral-slate">
            <Check className="h-5 w-5 text-secondary flex-shrink-0" />
            <span>{benefit}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
};

export default ModuleCard;
