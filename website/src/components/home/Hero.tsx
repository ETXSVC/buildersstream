import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle } from 'lucide-react';

const stats = [
  { value: '19+',   label: 'Modules'        },
  { value: '200+',  label: 'API Endpoints'  },
  { value: '100+',  label: 'Data Models'    },
  { value: '74',    label: 'E2E Tests'      },
];

const checks = [
  'Lead capture to final invoice',
  'Real-time field operations',
  'Payroll & certified reports',
];

const Hero = () => (
  <div className="relative overflow-hidden bg-[#0D0F1E] pt-24 pb-0 sm:pt-32">
    {/* Grid pattern */}
    <div
      className="absolute inset-0 opacity-20"
      style={{
        backgroundImage:
          'linear-gradient(to right,#7C3AED18 1px,transparent 1px),linear-gradient(to bottom,#7C3AED18 1px,transparent 1px)',
        backgroundSize: '40px 40px',
      }}
    />
    {/* Glow blobs */}
    <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl -translate-y-1/2" />
    <div className="absolute top-1/3 right-0 w-72 h-72 bg-violet-800/15 rounded-full blur-3xl" />

    <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-violet-600/10 border border-violet-500/20 text-violet-400 px-4 py-1.5 rounded-full text-xs sm:text-sm font-medium mb-6 sm:mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-400" />
            </span>
            Now live — beta access open
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.1]">
            Run Every Job.<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-violet-600">
              One Platform.
            </span>
          </h1>

          <p className="text-base sm:text-lg md:text-xl text-slate-400 mb-8 max-w-2xl mx-auto leading-relaxed">
            Replace 10 disconnected tools with one powerful construction OS. From first contact to final payment — manage everything in one place.
          </p>

          {/* Checks */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 mb-10">
            {checks.map((c) => (
              <div key={c} className="flex items-center gap-2 text-sm text-slate-400">
                <CheckCircle className="h-4 w-4 text-violet-400 shrink-0" />
                {c}
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="https://app.buildersstream.online/login"
              className="w-full sm:w-auto flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-xl font-semibold text-base transition-all shadow-lg shadow-violet-600/30 hover:shadow-violet-500/40"
            >
              Start Free Trial <ArrowRight className="h-4 w-4" />
            </a>
            <Link
              to="/features"
              className="w-full sm:w-auto flex items-center justify-center gap-2 border border-white/10 text-slate-300 hover:text-white hover:border-white/20 px-8 py-4 rounded-xl font-medium text-base transition-all"
            >
              See All Features
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-white/8 rounded-2xl overflow-hidden mt-16 sm:mt-20 border border-white/8"
        >
          {stats.map((s) => (
            <div key={s.label} className="bg-[#131629] py-6 px-4 text-center">
              <div className="text-2xl sm:text-3xl font-bold text-white">{s.value}</div>
              <div className="text-xs sm:text-sm text-slate-500 mt-1">{s.label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Dashboard preview */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="mt-12 sm:mt-16 relative mx-auto max-w-6xl"
      >
        <div className="relative rounded-t-2xl overflow-hidden border border-white/8 border-b-0 shadow-2xl shadow-black/60">
          {/* Fake browser chrome */}
          <div className="flex items-center gap-1.5 px-4 py-3 bg-[#1a1d30] border-b border-white/8">
            <span className="w-3 h-3 rounded-full bg-red-500/70" />
            <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <span className="w-3 h-3 rounded-full bg-green-500/70" />
            <div className="ml-3 flex-1 max-w-xs bg-[#0D0F1E] rounded px-3 py-1 text-xs text-slate-500 text-center">
              app.buildersstream.online
            </div>
          </div>
          <img
            src="/dashboard-preview.png"
            alt="BuilderStream Dashboard"
            className="w-full h-auto object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          {/* Gradient fade at bottom */}
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0D0F1E] to-transparent" />
        </div>
      </motion.div>
    </div>
  </div>
);

export default Hero;
