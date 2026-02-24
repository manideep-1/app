import React from 'react';
import { Link } from 'react-router-dom';
import IfElseIcon from '@/components/IfElseIcon';
import { Zap, Trophy, Users, Youtube, Linkedin, Twitter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

const LandingPage = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
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
            <div className="flex items-center gap-4">
              <Link to="/problems" data-testid="nav-problems-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  Problems
                </Button>
              </Link>
              {user ? (
                <>
                  <Link to="/compiler" data-testid="nav-compiler-link">
                    <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                      Compiler
                    </Button>
                  </Link>
                  <Link to="/dashboard" data-testid="nav-dashboard-link">
                    <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                      Dashboard
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    className="border-input hover:bg-accent hover:text-accent-foreground"
                    onClick={() => logout()}
                    data-testid="nav-logout-btn"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login" data-testid="nav-login-link">
                    <Button variant="outline" className="border-input hover:bg-accent hover:text-accent-foreground">
                      Login
                    </Button>
                  </Link>
                  <Link to="/register" data-testid="nav-register-link">
                    <Button className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-secondary/5 to-accent/10 blur-3xl"></div>
        <div className="container mx-auto px-6 md:px-12 lg:px-24 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
            <div className="md:col-span-7 space-y-8">
              <h1 className="font-heading font-bold text-5xl md:text-7xl tracking-tight leading-none">
                Master Coding
                <span className="block bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
                  Interviews
                </span>
              </h1>
              <p className="font-body text-lg md:text-xl leading-relaxed text-muted-foreground max-w-2xl">
                Practice on 500+ curated problems. Get hired by top tech companies. 
                Elevate your problem-solving skills with ifelse.
              </p>
              <div className="flex flex-wrap gap-4">
                {user ? (
                  <>
                    <Link to="/problems" data-testid="hero-get-started-btn">
                      <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300">
                        Go to Problems
                      </Button>
                    </Link>
                    <Link to="/compiler" data-testid="hero-compiler-btn">
                      <Button size="lg" variant="outline" className="border-input hover:bg-accent hover:text-accent-foreground">
                        Compiler
                      </Button>
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/register" data-testid="hero-get-started-btn">
                      <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300">
                        Start Practicing Free
                      </Button>
                    </Link>
                    <Link to="/problems" data-testid="hero-explore-problems-btn">
                      <Button size="lg" variant="outline" className="border-input hover:bg-accent hover:text-accent-foreground">
                        Explore Problems
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="md:col-span-5">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 blur-3xl rounded-full"></div>
                <img
                  src="https://images.unsplash.com/photo-1748375548801-a78f33241b03?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2ODl8MHwxfHNlYXJjaHwyfHxhYnN0cmFjdCUyMGRpZ2l0YWwlMjBsb2dpYyUyMGZsb3clMjB2aWJyYW50fGVufDB8fHx8MTc3MDgzMTA1NXww&ixlib=rb-4.1.0&q=85"
                  alt="Coding"
                  className="relative rounded-2xl shadow-2xl border border-border/50"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-card/30">
        <div className="container mx-auto px-6 md:px-12 lg:px-24">
          <div className="text-center mb-16">
            <h2 className="font-heading font-semibold text-3xl md:text-5xl tracking-tight mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="font-body text-base md:text-lg text-muted-foreground max-w-2xl mx-auto">
              Built for developers who want to ace their coding interviews
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<IfElseIcon className="w-8 h-8" />}
              title="Real-time Code Execution"
              description="Run your code instantly with our blazing-fast execution engine"
              color="primary"
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8" />}
              title="Instant Feedback"
              description="Get immediate results and detailed test case analysis"
              color="secondary"
            />
            <FeatureCard
              icon={<Trophy className="w-8 h-8" />}
              title="Track Progress"
              description="Monitor your growth with comprehensive stats and heatmaps"
              color="accent"
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Company Problems"
              description="Practice questions asked by top tech companies"
              color="primary"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-6 md:px-12 lg:px-24">
          <div className="bg-gradient-to-br from-primary/20 via-secondary/10 to-accent/20 rounded-3xl p-12 md:p-16 text-center border border-border/50">
            <h2 className="font-heading font-semibold text-3xl md:text-5xl tracking-tight mb-6">
              Ready to Level Up?
            </h2>
            <p className="font-body text-base md:text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              Join thousands of developers mastering their coding interview skills
            </p>
            {user ? (
              <Link to="/problems" data-testid="cta-problems-btn">
                <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300">
                  Go to Problems
                </Button>
              </Link>
            ) : (
              <Link to="/register" data-testid="cta-register-btn">
                <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300">
                  Start Your Journey
                </Button>
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Footer - four columns: Links, Social, Contact, Legal */}
      <footer className="border-t border-border/50 bg-card/50 py-12 md:py-14">
        <div className="container mx-auto px-6 md:px-12 lg:px-24">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-16">
            {/* Links */}
            <div>
              <h3 className="font-heading font-bold text-foreground mb-4">Links</h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/problems" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Problems
                  </Link>
                </li>
                <li>
                  <Link to="/compiler" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Compiler
                  </Link>
                </li>
                <li>
                  <Link to="/dashboard" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <a
                    href="https://github.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:text-primary/80 transition-colors"
                  >
                    How to use ifelse effectively
                  </a>
                </li>
              </ul>
            </div>
            {/* Social */}
            <div>
              <h3 className="font-heading font-bold text-foreground mb-4">Social</h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="https://youtube.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
                  >
                    <Youtube className="w-4 h-4 text-red-500" />
                    YouTube
                  </a>
                </li>
                <li>
                  <a
                    href="https://linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
                  >
                    <Linkedin className="w-4 h-4" />
                    LinkedIn
                  </a>
                </li>
                <li>
                  <a
                    href="https://twitter.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
                  >
                    <Twitter className="w-4 h-4" />
                    Twitter
                  </a>
                </li>
              </ul>
            </div>
            {/* Contact */}
            <div>
              <h3 className="font-heading font-bold text-foreground mb-4">Contact</h3>
              <a
                href="mailto:support@ifelse.io"
                className="text-sm text-foreground hover:text-primary transition-colors"
              >
                support@ifelse.io
              </a>
            </div>
            {/* Legal */}
            <div>
              <h3 className="font-heading font-bold text-foreground mb-4">Legal</h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/privacy" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="/terms" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <IfElseIcon className="w-5 h-5 text-primary" />
              <span className="font-heading font-bold text-lg text-foreground">If Else</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} If Else. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, description, color }) => {
  const colorClasses = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    accent: 'text-accent',
  };

  return (
    <div className="bg-card text-card-foreground border border-border/50 shadow-xl backdrop-blur-sm rounded-lg p-6 hover:border-primary/50 hover:shadow-[0_0_30px_rgba(99,102,241,0.15)] transition-all duration-300">
      <div className={`${colorClasses[color]} mb-4`}>{icon}</div>
      <h3 className="font-heading font-medium text-xl md:text-2xl mb-2">{title}</h3>
      <p className="font-body text-sm text-muted-foreground">{description}</p>
    </div>
  );
};

export default LandingPage;
