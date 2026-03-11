import React from 'react';
import { Link } from 'react-router-dom';
import IfElseIcon from '@/components/IfElseIcon';
import { Button } from '@/components/ui/button';

const PrivacyPage = () => {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 backdrop-blur-xl bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-6 md:px-12 lg:px-24 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <IfElseIcon className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-2xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
                If Else
              </span>
            </Link>
            <Link to="/">
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 md:px-12 lg:px-24 py-12 md:py-16 max-w-3xl">
        <h1 className="font-heading font-bold text-3xl md:text-4xl mb-2">Privacy Policy</h1>
        <p className="text-sm text-muted-foreground mb-10">
          Last updated: {new Date().toLocaleDateString('en-US')}
        </p>

        <div className="prose prose-neutral dark:prose-invert max-w-none space-y-8 text-muted-foreground">
          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">1. Information We Collect</h2>
            <p className="text-sm leading-relaxed">
              We collect information you provide when you register (email, name), when you use our services (code submissions, progress, and activity), and technical data such as IP address and browser type. We use this to operate the platform, improve your experience, and communicate with you.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">2. How We Use Your Information</h2>
            <p className="text-sm leading-relaxed">
              Your data is used to provide and personalize the If Else service, track your progress, run code execution, send transactional emails, and improve our product. We do not sell your personal information to third parties.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">3. Data Security</h2>
            <p className="text-sm leading-relaxed">
              We use industry-standard measures to protect your data, including encryption in transit and secure storage. You are responsible for keeping your account credentials confidential.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">4. Cookies and Similar Technologies</h2>
            <p className="text-sm leading-relaxed">
              We use cookies and similar technologies for authentication, preferences, and analytics to improve our service. You can manage cookie settings in your browser.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">5. Your Rights</h2>
            <p className="text-sm leading-relaxed">
              Depending on your location, you may have rights to access, correct, delete, or export your personal data. Contact us at support@ifelse.io to exercise these rights.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">6. Contact</h2>
            <p className="text-sm leading-relaxed">
              For privacy-related questions, contact us at{' '}
              <a href="mailto:support@ifelse.io" className="text-primary hover:underline">
                support@ifelse.io
              </a>.
            </p>
          </section>
        </div>

        <div className="mt-12 pt-8 border-t border-border/50">
          <Link to="/" className="text-primary hover:underline text-sm">← Back to Home</Link>
        </div>
      </main>
    </div>
  );
};

export default PrivacyPage;
