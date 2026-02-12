import { Link } from 'react-router-dom';
import React from 'react';
// ... your other imports
import Hero from '../components/home/Hero';
import FeatureGrid from '../components/home/FeatureGrid';

const Home = () => {
  return (
    <>
      <Hero />
      <FeatureGrid />
      


      {/* CTA Section */}
      <section className="py-24 bg-[#020617] relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        <div className="relative max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Ready to Streamline Your Business?</h2>
            <p className="text-lg text-neutral-300 mb-10">Join thousands of contractors saving 20+ hours a week with Builders Stream Pro.</p>
<Link 
  to="/contact" 
  className="bg-secondary hover:bg-secondary-hover text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-orange-500/20 inline-block"
>
  Find out more!
</Link>
        </div>
      </section>
    </>
  );
};

export default Home;
