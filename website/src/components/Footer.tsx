import React from 'react';
import { Link } from 'react-router-dom';
import { Github, Twitter, Linkedin, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-[#020617] text-white pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-8 mb-12">
          {/* Brand */}
          <div className="col-span-1 md:col-span-1">
            <Link to="/" className="flex items-center mb-6">
              <img src="/BuildersStream-Logo-tag.png" alt="Builders Stream Pro" className="h-10" />
            </Link>
            <p className="text-neutral-400 text-sm leading-relaxed mb-6">
              The unified operating system for modern construction. Replace 12 tools with 1 powerful platform.
            </p>
            <div className="flex space-x-4">
              <a href="https://github.com/ETXSVC/buildersstream" className="text-neutral-400 hover:text-white transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="https://twitter.com/@etxsvc24567" className="text-neutral-400 hover:text-white transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              {/*<a href="https://linkedin.com/BuildersStream" className="text-neutral-400 hover:text-white transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>*/}
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-primary-light mb-4">Product</h3>
            <ul className="space-y-3">
              <li><Link to="/" className="text-neutral-400 hover:text-white text-sm transition-colors">Home</Link></li>
              <li><Link to="/features" className="text-neutral-400 hover:text-white text-sm transition-colors">Features</Link></li>
              <li><Link to="/pricing" className="text-neutral-400 hover:text-white text-sm transition-colors">Pricing</Link></li>
              <li><Link to="/features#integrations" className="text-neutral-400 hover:text-white text-sm transition-colors">Integrations</Link></li>
              <li><Link to="/roadmap" className="text-neutral-400 hover:text-white text-sm transition-colors">Roadmap</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-primary-light mb-4">Company</h3>
            <ul className="space-y-3">
              <li><Link to="/about" className="text-neutral-400 hover:text-white text-sm transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="text-neutral-400 hover:text-white text-sm transition-colors">Contact</Link></li>
              <li><Link to="/careers" className="text-neutral-400 hover:text-white text-sm transition-colors">Careers</Link></li>
              <li><Link to="/blog" className="text-neutral-400 hover:text-white text-sm transition-colors">Blog</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-primary-light mb-4">Legal</h3>
            <ul className="space-y-3">
              <li><Link to="/privacy" className="text-neutral-400 hover:text-white text-sm transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="text-neutral-400 hover:text-white text-sm transition-colors">Terms of Service</Link></li>
              <li><Link to="/security" className="text-neutral-400 hover:text-white text-sm transition-colors">Security</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-neutral-800 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-neutral-500 text-sm">
            © {new Date().getFullYear()} Builders Stream Pro. All rights reserved.
          </p>
          <div className="flex items-center space-x-2 mt-4 md:mt-0">
            <Mail className="h-4 w-4 text-neutral-500" />
            <a href="mailto:hello@buildersstream.pro" className="text-neutral-500 hover:text-white text-sm transition-colors">
              hello@buildersstream.pro
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
