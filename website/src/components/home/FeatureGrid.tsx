import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Calendar,
  DollarSign,
  FileText,
  HardHat,
  Users,
  Shield,
  Zap,
  ClipboardList,
  Wrench,
} from 'lucide-react';

const features = [
  {
    title: 'Project Command Center',
    description:
      'Real-time dashboard for all your active jobs. Track progress, budgets, and timelines at a glance with health scoring.',
    icon: BarChart3,
  },
  {
    title: 'Smart Scheduling',
    description:
      'Drag-and-drop Gantt charts that automatically adjust dependent tasks when delays happen.',
    icon: Calendar,
  },
  {
    title: 'Financial Management',
    description:
      'Job costing, invoicing, expenses, change orders, and purchase orders — all in one place.',
    icon: DollarSign,
  },
  {
    title: 'Estimating & Proposals',
    description:
      'Build professional estimates in minutes. Convert accepted proposals to projects with one click.',
    icon: FileText,
  },
  {
    title: 'Field Operations',
    description:
      'Mobile-first daily logs, time tracking, photos, and safety reports. Keep the site connected to the office.',
    icon: HardHat,
  },
  {
    title: 'Crew & Team Management',
    description:
      'Manage workforce schedules, certifications, and time tracking. W-2 and 1099 contractors supported.',
    icon: Users,
  },
  {
    title: 'Quality & Safety',
    description:
      'Inspections, deficiency tracking, and safety incident reports. Stay compliant on every job.',
    icon: Shield,
  },
  {
    title: 'Issue Tracking & SLA',
    description:
      'Built-in issue tracker with SLA timers, escalation rules, and auto-assignment workflows.',
    icon: Zap,
  },
  {
    title: 'Documents & RFIs',
    description:
      'Document management, RFIs, submittals, and photo galleries — organized by project.',
    icon: ClipboardList,
  },
  {
    title: 'Service & Warranty',
    description:
      'Track service requests, warranties, and claims through close-out and beyond.',
    icon: Wrench,
  },
];

const FeatureGrid = () => {
  return (
    <section className="py-20 sm:py-28 bg-[#0D0F1E] relative overflow-hidden">
      {/* Background grid */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            'linear-gradient(#7C3AED 1px, transparent 1px), linear-gradient(90deg, #7C3AED 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />

      {/* Glow blob */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-violet-700/10 blur-[120px] pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section label */}
        <div className="flex justify-center mb-6">
          <span className="inline-flex items-center gap-2 bg-violet-900/40 border border-violet-700/40 text-violet-300 text-xs font-semibold uppercase tracking-widest px-4 py-1.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 inline-block" />
            Why BuilderStream
          </span>
        </div>

        <div className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-4 leading-tight">
            Every tool your crew needs.{' '}
            <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
              One platform.
            </span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            A modular system that grows with your business. 19 apps covering the
            entire construction lifecycle — from first lead to final invoice.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.07 }}
              className="group relative rounded-2xl border border-white/5 bg-white/[0.03] p-6 hover:bg-white/[0.06] hover:border-violet-500/30 transition-all duration-300"
            >
              {/* Icon */}
              <div className="mb-4 inline-flex items-center justify-center w-11 h-11 rounded-xl bg-violet-600/20 border border-violet-500/20 group-hover:bg-violet-600/30 transition-colors">
                <feature.icon className="h-5 w-5 text-violet-400" />
              </div>

              <h3 className="text-base font-bold text-white mb-2 group-hover:text-violet-300 transition-colors">
                {feature.title}
              </h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Stats bar */}
        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-6 border-t border-white/5 pt-12">
          {[
            { value: '19+', label: 'Integrated Modules' },
            { value: '200+', label: 'API Endpoints' },
            { value: '100+', label: 'Data Models' },
            { value: '74', label: 'E2E Tests Passing' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-extrabold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="text-slate-500 text-sm mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureGrid;
