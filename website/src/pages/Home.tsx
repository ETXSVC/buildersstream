import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Hero from '../components/home/Hero';
import FeatureGrid from '../components/home/FeatureGrid';

const Home = () => {
  return (
    <>
      <Hero />
      <FeatureGrid />

      {/* CTA Section */}
      <section className="py-20 sm:py-28 bg-[#0D0F1E] relative overflow-hidden">
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(#7C3AED 1px, transparent 1px), linear-gradient(90deg, #7C3AED 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
        {/* Glow */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[500px] h-[200px] bg-violet-700/20 blur-[80px] rounded-full pointer-events-none" />

        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            {/* Badge */}
            <span className="inline-flex items-center gap-2 bg-violet-900/40 border border-violet-700/40 text-violet-300 text-xs font-semibold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse inline-block" />
              Beta access open
            </span>

            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-5 leading-tight">
              Ready to streamline{' '}
              <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                your business?
              </span>
            </h2>
            <p className="text-slate-400 text-lg mb-10">
              Join contractors saving 20+ hours a week. One platform. Every job.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="https://app.buildersstream.online/login"
                className="w-full sm:w-auto bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-xl font-bold text-base transition-all shadow-lg shadow-violet-900/40 hover:shadow-violet-700/50"
              >
                Start Free Trial
              </a>
              <Link
                to="/contact"
                className="w-full sm:w-auto border border-white/10 hover:border-violet-500/50 text-slate-300 hover:text-white px-8 py-4 rounded-xl font-semibold text-base transition-all"
              >
                Contact Sales
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
};

export default Home;
