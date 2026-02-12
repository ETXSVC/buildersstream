import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Play, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const Hero = () => {
  return (
    <div className="relative overflow-hidden bg-neutral-light pt-16 pb-32 lg:pt-32 lg:pb-40">
      {/* Background Pattern */}
      <div className="absolute inset-0 z-0 bg-grid-pattern bg-[length:40px_40px] opacity-30" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-neutral-light/50 to-neutral-light z-0" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
          >
            <div className="inline-flex items-center space-x-2 bg-red-500/10 text-red-500 px-4 py-1.5 rounded-full text-2xl font-medium mb-8">
              <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              </span>
              <span>Currently in development Coming June 2026</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-neutral-slate mb-8 leading-tight">
              The Unified <span className="text-primary">Construction</span> <br className="hidden md:block" /> Operating System
            </h1>

            <p className="text-xl text-neutral-gray mb-10 max-w-2xl mx-auto leading-relaxed">
              Replace 10 disconnected tools with one powerful platform. From lead capture to final punchlist, run your entire construction business in one place.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link
                to="/contact"
                className="w-full sm:w-auto bg-[#ef4444] hover:bg-[#dc2626] text-white border border-transparent px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-red-500/25 flex items-center justify-center space-x-2"
              >
                <span>Join our Beta Test waiting list</span>
              </Link>
            </div>


          </motion.div>
        </div>

        {/* Dashboard Preview / Floating UI Elements */}
        <motion.div
           initial={{ opacity: 0, y: 40 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.7, delay: 0.2 }}
           className="mt-20 relative mx-auto max-w-6xl"
        >
            <div className="relative rounded-2xl bg-neutral-slate p-2 shadow-2xl ring-1 ring-gray-900/10">
                <div className="absolute -top-12 -left-12 w-24 h-24 bg-secondary rounded-full blur-2xl opacity-20 animate-pulse"></div>
                <div className="absolute -bottom-12 -right-12 w-32 h-32 bg-primary rounded-full blur-3xl opacity-20"></div>
                
                <div className="relative rounded-xl overflow-hidden shadow-2xl border border-neutral-800 bg-[#1e293b]">
                    <img 
                        src="/dashboard-preview.png" 
                        alt="Builders Stream Pro Dashboard Interface" 
                        className="w-full h-auto object-cover"
                    />
                </div>
            </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Hero;
