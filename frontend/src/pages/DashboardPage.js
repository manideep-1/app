import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Code2, LogOut, TrendingUp, CheckCircle2, Clock } from 'lucide-react';
import { toast } from 'sonner';

const DashboardPage = () => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProgress();
  }, [user]);

  const fetchProgress = async () => {
    try {
      const response = await api.get('/user/progress');
      setProgress(response.data);
    } catch (error) {
      toast.error('Failed to load progress');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border/50 backdrop-blur-xl bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-6 md:px-12 lg:px-24 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <Code2 className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-2xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
                ifelse
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/problems" data-testid="nav-problems-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  Problems
                </Button>
              </Link>
              <Button
                variant="outline"
                onClick={handleLogout}
                data-testid="logout-btn"
                className="border-input hover:bg-destructive hover:text-destructive-foreground"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-6 md:px-12 lg:px-24 py-12">
        <div className="mb-8">
          <h1 className="font-heading font-bold text-4xl md:text-5xl mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-muted-foreground text-lg">Track your coding journey</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading your progress...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                icon={<CheckCircle2 className="w-8 h-8" />}
                title="Total Solved"
                value={progress?.total_solved || 0}
                color="primary"
              />
              <StatCard
                icon={<TrendingUp className="w-8 h-8" />}
                title="Total Submissions"
                value={progress?.total_submissions || 0}
                color="secondary"
              />
              <StatCard
                icon={<CheckCircle2 className="w-8 h-8" />}
                title="Easy Solved"
                value={progress?.easy_solved || 0}
                color="accent"
                subtitle={`${progress?.easy_solved || 0} problems`}
              />
              <StatCard
                icon={<Clock className="w-8 h-8" />}
                title="Medium + Hard"
                value={(progress?.medium_solved || 0) + (progress?.hard_solved || 0)}
                color="primary"
                subtitle={`${progress?.medium_solved || 0} medium, ${progress?.hard_solved || 0} hard`}
              />
            </div>

            {/* Progress Breakdown */}
            <div className="bg-card border border-border/50 rounded-lg p-8 shadow-xl" data-testid="progress-breakdown">
              <h2 className="font-heading font-semibold text-2xl mb-6">Progress by Difficulty</h2>
              <div className="space-y-6">
                <ProgressBar
                  label="Easy"
                  value={progress?.easy_solved || 0}
                  total={100}
                  color="green"
                />
                <ProgressBar
                  label="Medium"
                  value={progress?.medium_solved || 0}
                  total={100}
                  color="yellow"
                />
                <ProgressBar
                  label="Hard"
                  value={progress?.hard_solved || 0}
                  total={50}
                  color="red"
                />
              </div>
            </div>

            {/* CTA */}
            <div className="bg-gradient-to-br from-primary/20 via-secondary/10 to-accent/20 rounded-3xl p-12 text-center border border-border/50">
              <h2 className="font-heading font-semibold text-3xl mb-4">
                Keep Going!
              </h2>
              <p className="text-muted-foreground mb-6">
                {progress?.total_solved === 0
                  ? 'Start solving problems to track your progress'
                  : `You've solved ${progress?.total_solved} problems. Keep up the momentum!`}
              </p>
              <Link to="/problems" data-testid="continue-practicing-btn">
                <Button
                  size="lg"
                  className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300"
                >
                  Continue Practicing
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ icon, title, value, color, subtitle }) => {
  const colorClasses = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    accent: 'text-accent',
  };

  return (
    <div className="bg-card text-card-foreground border border-border/50 shadow-xl backdrop-blur-sm rounded-lg p-6 hover:border-primary/50 hover:shadow-[0_0_30px_rgba(99,102,241,0.15)] transition-all duration-300">
      <div className={`${colorClasses[color]} mb-4`}>{icon}</div>
      <h3 className="font-body text-sm text-muted-foreground mb-1">{title}</h3>
      <p className="font-heading font-bold text-3xl">{value}</p>
      {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
    </div>
  );
};

const ProgressBar = ({ label, value, total, color }) => {
  const percentage = Math.min((value / total) * 100, 100);
  
  const colorClasses = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium">{label}</span>
        <span className="text-sm text-muted-foreground">
          {value} / {total}
        </span>
      </div>
      <div className="h-3 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default DashboardPage;
