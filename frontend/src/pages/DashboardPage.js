import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import IfElseIcon from '@/components/IfElseIcon';
import { LogOut, TrendingUp, CheckCircle2, Clock, Flame } from 'lucide-react';
import { toast } from 'sonner';
const currentYear = new Date().getFullYear();

const DashboardPage = () => {
  const [progress, setProgress] = useState(null);
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const { user, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProgress();
    fetchActivity(selectedYear);
  }, [user, authLoading]);

  useEffect(() => {
    if (!user) return;
    fetchActivity(selectedYear);
  }, [selectedYear, user]);

  // Refetch activity when user returns to dashboard (e.g. after submitting) so streak updates
  useEffect(() => {
    if (!user) return;
    const onFocus = () => {
      fetchProgress();
      fetchActivity(selectedYear);
    };
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [user, selectedYear]);

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

  const fetchActivity = async (year) => {
    try {
      const response = await api.get('/user/activity', { params: { year } });
      setActivity(response.data);
    } catch {
      setActivity({
        submission_dates: [],
        dates_count: {},
        current_streak: 0,
        longest_streak: 0,
        year: year,
        available_years: [currentYear, currentYear - 1, currentYear - 2, currentYear - 3, currentYear - 4],
      });
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

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
              <Link to="/my-plan" data-testid="nav-my-plan-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  My Plan
                </Button>
              </Link>
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
                color="primary"
              />
              <StatCard
                icon={<CheckCircle2 className="w-8 h-8" />}
                title="Easy Solved"
                value={progress?.easy_solved || 0}
                color="primary"
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

            {/* Streak & Activity */}
            {activity && (
              <div className="bg-card border border-border/50 rounded-lg p-8 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <h2 className="font-heading font-semibold text-2xl flex items-center gap-2">
                    <Flame className="w-7 h-7 text-orange-400" />
                    Your Streak
                  </h2>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground mr-2">Year:</span>
                    {(activity.available_years || [currentYear, currentYear - 1, currentYear - 2, currentYear - 3, currentYear - 4]).map((y) => (
                      <Button
                        key={y}
                        variant={selectedYear === y ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedYear(y)}
                        className={selectedYear === y ? 'bg-primary' : ''}
                      >
                        {y}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="flex flex-wrap gap-8 mb-6">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      {selectedYear === currentYear ? 'Current streak' : `Streak at end of ${selectedYear}`}
                    </p>
                    <p className="font-heading font-bold text-3xl text-orange-400">{activity.current_streak} day{activity.current_streak !== 1 ? 's' : ''}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Longest streak in {activity.year}</p>
                    <p className="font-heading font-bold text-3xl text-muted-foreground">{activity.longest_streak} day{activity.longest_streak !== 1 ? 's' : ''}</p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-2">Submission activity in {activity.year} (like GitHub contributions)</p>
                <ActivityCalendarYear datesSet={new Set(activity.submission_dates || [])} year={activity.year} />
              </div>
            )}

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
            <div className="bg-gradient-to-br from-primary/20 via-secondary/10 to-primary/20 rounded-3xl p-12 text-center border border-border/50">
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
                  className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(37,99,235,0.5)] transition-all duration-300"
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

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** GitHub-style full-year activity grid: 7 rows (Sun–Sat), columns grouped by month with spacing. */
const ActivityCalendarYear = ({ datesSet, year }) => {
  const jan1 = new Date(year, 0, 1);
  const dec31 = new Date(year, 11, 31);
  const start = new Date(jan1);
  start.setDate(jan1.getDate() - jan1.getDay());
  const end = new Date(dec31);
  end.setDate(dec31.getDate() + (6 - dec31.getDay()));
  const totalDays = Math.round((end - start) / (24 * 60 * 60 * 1000)) + 1;
  const numWeeks = Math.ceil(totalDays / 7);

  const grid = Array(7)
    .fill(null)
    .map(() => Array(numWeeks).fill(null));
  const cursor = new Date(start);
  for (let i = 0; i < totalDays; i++) {
    const dayOfWeek = cursor.getDay();
    const weekIndex = Math.floor(i / 7);
    const key = cursor.toISOString().slice(0, 10);
    if (cursor >= jan1 && cursor <= dec31) {
      grid[dayOfWeek][weekIndex] = { key, active: datesSet.has(key) };
    }
    cursor.setDate(cursor.getDate() + 1);
  }

  // First week index that contains any day of each month (for grouping and labels)
  const firstWeekOfMonth = [];
  for (let m = 0; m < 12; m++) {
    const firstDay = new Date(year, m, 1);
    let wi = 0;
    for (; wi < numWeeks; wi++) {
      const weekStart = new Date(start);
      weekStart.setDate(weekStart.getDate() + wi * 7);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);
      if (weekStart <= firstDay && firstDay <= weekEnd) break;
      if (weekStart > firstDay) break;
    }
    firstWeekOfMonth[m] = Math.min(wi, numWeeks);
  }

  // Build month blocks: each block is { monthIndex, weekStart, weekEnd }
  const monthBlocks = [];
  for (let m = 0; m < 12; m++) {
    const weekStart = firstWeekOfMonth[m];
    const weekEnd = m < 11 ? firstWeekOfMonth[m + 1] - 1 : numWeeks - 1;
    if (weekStart <= weekEnd) monthBlocks.push({ monthIndex: m, weekStart, weekEnd });
  }

  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const cellSize = 'w-3 h-3';
  const gap = 'gap-0.5';

  return (
    <div className="overflow-x-auto">
      <div className="inline-flex min-w-0" style={{ alignItems: 'stretch' }}>
        {/* Day labels column: one spacer row (aligns with month row) + 7 day rows */}
        <div className={`flex flex-col ${gap} shrink-0 pr-2`}>
          <div className={cellSize} aria-hidden="true" />
          {dayLabels.map((d) => (
            <div key={d} className={`${cellSize} flex items-center justify-end`}>
              <span className="text-[10px] text-muted-foreground leading-none">{d}</span>
            </div>
          ))}
        </div>
        {/* Month blocks + grid: same row structure so labels align */}
        <div className="flex gap-4">
          {monthBlocks.map(({ monthIndex, weekStart, weekEnd }) => (
            <div key={monthIndex} className={`flex flex-col ${gap}`}>
              <div className={`${cellSize} flex items-center`}>
                <span className="text-[10px] text-muted-foreground leading-none">
                  {MONTH_NAMES[monthIndex]}
                </span>
              </div>
              <div className={`flex ${gap}`}>
                {Array.from({ length: weekEnd - weekStart + 1 }, (_, i) => weekStart + i).map((wi) => (
                  <div key={wi} className={`flex flex-col ${gap}`}>
                    {Array.from({ length: 7 }, (_, di) => {
                      const cell = grid[di][wi];
                      if (!cell) return <div key={di} className={`${cellSize} rounded-sm bg-transparent shrink-0`} />;
                      return (
                        <div
                          key={cell.key}
                          title={`${cell.key}${cell.active ? ' • activity' : ''}`}
                          className={`${cellSize} rounded-sm shrink-0 ${cell.active ? 'bg-primary' : 'bg-muted/50'}`}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
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
    <div className="bg-card text-card-foreground border border-border/50 shadow-xl backdrop-blur-sm rounded-lg p-6 hover:border-primary/50 hover:shadow-[0_0_30px_rgba(37,99,235,0.15)] transition-all duration-300">
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
