import React from 'react';

const About = () => {
  return (
    <div className="bg-[#0f172a] min-h-screen">
      <div className="max-w-4xl mx-auto px-4 py-24">
        <h1 className="text-4xl md:text-5xl font-bold text-neutral-slate mb-8">Built by Builders, For Builders</h1>
        
        <div className="prose prose-lg text-neutral-gray text-lg leading-relaxed space-y-8">
            <p>
                Builders Stream Pro wasn't born in a Silicon Valley boardroom. It was built on job sites, in dusty trucks, and during late-night estimating sessions at the kitchen table.
            </p>
            
            <h3 className="text-2xl font-bold text-neutral-slate">The "Muddy Glove" Test</h3>
            <p>
                Our core philosophy is simple: if a feature can't be used by a contractor wearing muddy gloves on a job site, it doesn't belong in our app. We believe software should serve the field, not the other way around.
            </p>

            <h3 className="text-2xl font-bold text-neutral-slate">The Unified Vision</h3>
            <p>
                For too long, contractors have been forced to stitch together 10 different apps to run their business. 
                One for scheduling, one for estimates, another for chat, and yet another for time tracking. 
                Data gets lost, communication breaks down, and mistakes happen.
            </p>
            <p>
                Builders Stream Pro v3.0 changes that. We are the <strong>Unified Construction Operating System</strong>. 
                One login, one source of truth, one seamless workflow.
            </p>
        </div>
      </div>
    </div>
  );
};

export default About;
