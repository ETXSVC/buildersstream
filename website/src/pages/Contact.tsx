import React from 'react';
import { Mail, Phone, MapPin } from 'lucide-react';

const Contact = () => {
  return (
    <div className="bg-neutral-light min-h-screen py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
            
            {/* Contact Info */}
            <div>
                <h1 className="text-4xl font-bold text-neutral-slate mb-6">Let's Build Together</h1>
                <p className="text-xl text-neutral-gray mb-12">
                    Have questions about the platform? Want a custom demo for your enterprise team? We're here to help.
                </p>

                <div className="space-y-8">
                    <div className="flex items-start space-x-4">
                        <div className="bg-[#1e293b] p-3 rounded-lg shadow-sm">
                            <Mail className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-bold text-neutral-slate">Email Us</h3>
                            <p className="text-neutral-500">info@buildersstream.pro</p>
                            <p className="text-neutral-500">beta-list@buildersstream.pro</p>
                        </div>
                    </div>
                    
                    <div className="flex items-start space-x-4">
                         <div className="bg-[#1e293b] p-3 rounded-lg shadow-sm">
                            <Phone className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-bold text-neutral-slate">Call Us</h3>
                            <p className="text-neutral-500">+1 (430) 344-1499</p>
                            <p className="text-sm text-neutral-400">Mon-Fri, 9am - 6pm CST</p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-4">
                         <div className="bg-[#1e293b] p-3 rounded-lg shadow-sm">
                            <MapPin className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-bold text-neutral-slate">Headquarters</h3>
                            <p className="text-neutral-500">Chandler, TX 75758</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Form */}
            <div className="bg-[#1e293b] rounded-2xl shadow-xl p-8 border border-neutral-800">
                <form className="space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-neutral-300 mb-2">First Name</label>
                            <input type="text" className="w-full px-4 py-3 rounded-lg border border-neutral-700 bg-[#0f172a] text-white focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-neutral-600" placeholder="John" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-neutral-300 mb-2">Last Name</label>
                            <input type="text" className="w-full px-4 py-3 rounded-lg border border-neutral-700 bg-[#0f172a] text-white focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-neutral-600" placeholder="Doe" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">Email Address</label>
                        <input type="email" className="w-full px-4 py-3 rounded-lg border border-neutral-700 bg-[#0f172a] text-white focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-neutral-600" placeholder="john@company.com" />
                    </div>

                    <div>
                         <label className="block text-sm font-medium text-neutral-300 mb-2">Company Name</label>
                         <input type="text" className="w-full px-4 py-3 rounded-lg border border-neutral-700 bg-[#0f172a] text-white focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-neutral-600" placeholder="Acme Construction" />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">Message</label>
                        <textarea rows={4} className="w-full px-4 py-3 rounded-lg border border-neutral-700 bg-[#0f172a] text-white focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-neutral-600" placeholder="Tell us about your needs..." />
                    </div>

                    <button type="submit" className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-primary/20">
                        Send Message
                    </button>
                </form>
            </div>

        </div>
      </div>
    </div>
  );
};

export default Contact;
