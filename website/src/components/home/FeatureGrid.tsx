import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Users, DollarSign, FileText, BarChart3, HardHat } from 'lucide-react';

const features = [
  {
    title: 'Project Command Center',
    description: 'Real-time dashboard for all your active jobs. Track progress, budgets, and timelines at a glance.',
    icon: BarChart3,
    color: 'bg-blue-500',
    colSpan: 'lg:col-span-2',
  },
  {
    title: 'Smart Scheduling',
    description: 'Drag-and-drop Gantt charts that automatically adjust dependent tasks when delays happen.',
    icon: Calendar,
    color: 'bg-orange-500',
    colSpan: 'lg:col-span-1',
  },
  {
    title: 'Financial Management',
    description: 'Job costing, invoicing, and expenses. Integrated with QuickBooks for seamless accounting.',
    icon: DollarSign,
    color: 'bg-green-500',
    colSpan: 'lg:col-span-1',
  },
  {
    title: 'Crew & Subcoms',
    description: 'Manage workforce schedules, certifications, and time tracking. Communication portal for subcontractors.',
    icon: Users,
    color: 'bg-purple-500',
    colSpan: 'lg:col-span-2',
  },
  {
    title: 'Estimating & Takeoffs',
    description: 'Create professional estimates in minutes. Convert accepted estimates to projects with one click.',
    icon: FileText,
    color: 'bg-red-500',
    colSpan: 'lg:col-span-1',
  },
  {
    title: 'Field Operations',
    description: 'Mobile-first daily logs, photos, and safety reports. Keep the site connected to the office.',
    icon: HardHat,
    color: 'bg-yellow-500',
    colSpan: 'lg:col-span-2', // Filler to make grid nice, adjusted below
  },
];

const FeatureGrid = () => {
  return (
    <section className="py-16 sm:py-24 bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10 sm:mb-16">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-neutral-slate mb-4">Everything You Need to Build Better</h2>
        <p className="text-lg sm:text-xl md:text-2xl text-blue-500 max-w-2xl mx-auto">
            A modular system that grows with your business. Turn features on or off as you need them.
        </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 auto-rows-[minmax(180px,auto)] sm:auto-rows-[minmax(200px,auto)]">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`group relative overflow-hidden rounded-2xl border border-neutral-800 bg-[#1e293b] p-6 sm:p-8 hover:shadow-lg transition-all duration-300 ${feature.colSpan}`}
            >
              <div className={`absolute top-0 right-0 w-32 h-32 opacity-5 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-150 ${feature.color}`} />
              
              <div className={`inline-flex items-center justify-center p-3 rounded-xl ${feature.color} bg-opacity-10 text-${feature.color.replace('bg-', '')} mb-6`}>
                <feature.icon className={`h-6 w-6 ${feature.color.replace('bg-', 'text-')}`} />
              </div>

              <h3 className="text-xl font-bold text-neutral-slate mb-3 group-hover:text-primary transition-colors">
                {feature.title}
              </h3>
              <p className="text-neutral-gray leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureGrid;
