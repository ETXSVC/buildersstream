import React from 'react';

const Privacy = () => {
  return (
    <div className="bg-[#0f172a] min-h-screen">
      <div className="max-w-4xl mx-auto px-4 py-24">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-8">Privacy Policy</h1>
        <p className="text-neutral-400 mb-12">Last updated: {new Date().toLocaleDateString()}</p>
        
        <div className="prose prose-lg prose-invert text-neutral-300 leading-relaxed space-y-8">
            <section>
                <h3 className="text-2xl font-bold text-white mb-4">1. Introduction</h3>
                <p>
                    Builders Stream Pro ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our unified construction management platform.
                </p>
            </section>

            <section>
                <h3 className="text-2xl font-bold text-white mb-4">2. Information We Collect</h3>
                <ul className="list-disc pl-6 space-y-2">
                    <li><strong>Account Information:</strong> Name, email address, company name, and payment information when you register.</li>
                    <li><strong>Project Data:</strong> Information related to your construction projects, including estimates, schedules, and client details managed through our platform.</li>
                    <li><strong>Usage Data:</strong> Information about how you interact with our services, including log files, device information, and IP addresses.</li>
                </ul>
            </section>

            <section>
                <h3 className="text-2xl font-bold text-white mb-4">3. How We Use Your Information</h3>
                <p>We use the collected information to:</p>
                <ul className="list-disc pl-6 space-y-2">
                    <li>Provide, operate, and maintain the Builders Stream Pro platform.</li>
                    <li>Process transactions and manage your subscription.</li>
                    <li>Send administrative information, updates, and security alerts.</li>
                    <li>Analyze usage patterns to improve our features and user experience.</li>
                </ul>
            </section>

            <section>
                <h3 className="text-2xl font-bold text-white mb-4">4. Data Security</h3>
                <p>
                    We implement industry-standard security measures to protect your data, including encryption in transit and at rest. However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.
                </p>
            </section>

             <section>
                <h3 className="text-2xl font-bold text-white mb-4">5. Contact Us</h3>
                <p>
                    If you have any questions about this Privacy Policy, please contact us at <a href="mailto:privacy@buildersstream.pro" className="text-primary hover:text-primary-light">privacy@buildersstream.pro</a>.
                </p>
            </section>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
