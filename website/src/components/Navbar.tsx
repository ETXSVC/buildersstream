import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => { setIsOpen(false); }, [location.pathname]);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Features', path: '/features' },
    { name: 'Pricing',  path: '/pricing'  },
    { name: 'About',    path: '/about'    },
    { name: 'Contact',  path: '/contact'  },
  ];

  return (
    <nav className={cn(
      'fixed top-0 w-full z-50 transition-all duration-300',
      scrolled
        ? 'bg-[#0D0F1E]/90 backdrop-blur-md border-b border-white/8 shadow-lg'
        : 'bg-transparent'
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-20">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center rotate-45 group-hover:bg-violet-500 transition-colors">
              <div className="-rotate-45 w-3 h-3 bg-white rounded-sm" />
            </div>
            <span className="text-white font-bold text-lg tracking-tight">BuildersStream</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={cn(
                  'text-sm font-medium transition-colors',
                  location.pathname === link.path
                    ? 'text-white'
                    : 'text-slate-400 hover:text-white'
                )}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Desktop CTAs */}
          <div className="hidden md:flex items-center gap-4">
            <a
              href="https://app.buildersstream.online/login"
              className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
            >
              Sign In
            </a>
            <Link
              to="/contact"
              className="bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-all hover:shadow-lg hover:shadow-violet-600/25"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-slate-400 hover:text-white transition-colors"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#131629] border-b border-white/8 overflow-hidden"
          >
            <div className="px-4 pt-3 pb-6 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'block px-3 py-3 rounded-lg text-sm font-medium transition-colors',
                    location.pathname === link.path
                      ? 'text-white bg-violet-600/10'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  )}
                >
                  {link.name}
                </Link>
              ))}
              <div className="pt-4 space-y-2">
                <a
                  href="https://app.buildersstream.online/login"
                  className="block w-full text-center border border-white/10 text-slate-300 px-5 py-3 rounded-lg text-sm font-medium hover:bg-white/5 transition-all"
                >
                  Sign In
                </a>
                <Link
                  to="/contact"
                  onClick={() => setIsOpen(false)}
                  className="block w-full text-center bg-violet-600 hover:bg-violet-500 text-white px-5 py-3 rounded-lg text-sm font-semibold transition-all"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
