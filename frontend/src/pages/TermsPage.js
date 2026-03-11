import React from 'react';
import { Link } from 'react-router-dom';
import IfElseIcon from '@/components/IfElseIcon';
import { Button } from '@/components/ui/button';

const TermsPage = () => {
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
        <h1 className="font-heading font-bold text-3xl md:text-4xl mb-2">Terms of Service</h1>
        <p className="text-sm text-muted-foreground mb-10">
          Last updated: {new Date().toLocaleDateString('en-US')}
        </p>

        <div className="prose prose-neutral dark:prose-invert max-w-none space-y-8 text-muted-foreground">
          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">1. Acceptance of Terms</h2>
            <p className="text-sm leading-relaxed">
              By accessing or using If Else (“the Service”), you agree to be bound by these Terms of Service. If you do not agree, do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">2. Use of the Service</h2>
            <p className="text-sm leading-relaxed">
              You may use If Else for personal learning and interview preparation. You must provide accurate registration information and keep your account secure. You may not use the Service for any illegal purpose, to abuse or overload our systems, or to attempt to gain unauthorized access.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">3. Code Execution and Content</h2>
            <p className="text-sm leading-relaxed">
              Code you submit is executed in a sandboxed environment. You retain ownership of your code. By submitting code, you grant us a license to run it for providing the Service and improving our systems. Do not submit malicious code or content that violates others’ rights.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">4. Intellectual Property</h2>
            <p className="text-sm leading-relaxed">
              If Else’s platform, design, and materials are owned by us or our licensors. Problem content may be sourced from third parties and is used under appropriate licenses. You may not copy, modify, or distribute our content without permission.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">5. Disclaimers</h2>
            <p className="text-sm leading-relaxed">
              The Service is provided “as is.” We do not guarantee uninterrupted or error-free operation. We are not liable for any decisions you make based on hints, solutions, or AI-generated content. Use the Service at your own risk.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">6. Limitation of Liability</h2>
            <p className="text-sm leading-relaxed">
              To the maximum extent permitted by law, If Else and its affiliates shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the Service.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">7. Changes and Termination</h2>
            <p className="text-sm leading-relaxed">
              We may update these Terms from time to time; continued use after changes constitutes acceptance. We may suspend or terminate your access for violation of these Terms or for any other reason.
            </p>
          </section>

          <section>
            <h2 className="font-heading font-semibold text-lg text-foreground mb-2">8. Contact</h2>
            <p className="text-sm leading-relaxed">
              For questions about these Terms, contact us at{' '}
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

export default TermsPage;
