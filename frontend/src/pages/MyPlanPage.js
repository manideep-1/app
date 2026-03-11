import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft, Loader2, RefreshCw, Target, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { DIFFICULTY_BG, DIFFICULTY_COLORS } from '@/utils/constants';

const STATUS_LABEL = {
  not_started: 'Not started',
  in_progress: 'In progress',
  completed: 'Completed',
};

const nextStatus = (current) => {
  if (current === 'completed') return 'not_started';
  if (current === 'in_progress') return 'completed';
  return 'in_progress';
};

export default function MyPlanPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState(null);
  const [updatingProblemId, setUpdatingProblemId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('coach/my-plan');
      setPlan(data?.plan || null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to load preparation plan');
      setPlan(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate('/login', { state: { from: '/my-plan' } });
      return;
    }
    loadPlan();
  }, [authLoading, user, navigate]);

  const updateProblemStatus = async (planProblemId, status) => {
    if (!planProblemId) return;
    setUpdatingProblemId(planProblemId);
    try {
      const { data } = await api.patch(`coach/my-plan/problems/${planProblemId}`, { status });
      setPlan(data?.plan || null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update plan progress');
    } finally {
      setUpdatingProblemId(null);
    }
  };

  const deletePlan = async () => {
    setDeleting(true);
    try {
      await api.delete('coach/my-plan');
      setPlan(null);
      toast.success('Preparation plan deleted');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete preparation plan');
    } finally {
      setDeleting(false);
    }
  };

  const totals = useMemo(() => {
    if (!plan) return { completed: 0, total: 0, percent: 0 };
    return {
      completed: plan.completedProblems || 0,
      total: plan.totalProblems || 0,
      percent: plan.overallCompletionPercent || 0,
    };
  }, [plan]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-6 md:px-12 lg:px-24 py-8 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Link to="/coach">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Coach
              </Button>
            </Link>
            <h1 className="font-heading font-semibold text-3xl">My Preparation Plan</h1>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/problems">
              <Button variant="outline" size="sm">Problems</Button>
            </Link>
            <Button variant="outline" size="sm" onClick={loadPlan}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            {plan && (
              <Button variant="outline" size="sm" className="border-destructive/50 text-destructive hover:bg-destructive/10" onClick={deletePlan} disabled={deleting}>
                <Trash2 className="w-4 h-4 mr-2" />
                {deleting ? 'Deleting...' : 'Delete Plan'}
              </Button>
            )}
          </div>
        </div>

        {!plan ? (
          <Card className="border-border/60 bg-card/30">
            <CardHeader>
              <CardTitle>No active plan yet</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Ask the Coach for a timeline-based prep plan (for example: "I have 2 weeks for Amazon SDE, 3 hours per day").
              </p>
              <Link to="/coach">
                <Button>
                  <Target className="w-4 h-4 mr-2" />
                  Create plan in Coach
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <>
            <Card className="border-border/60 bg-card/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">
                  {plan.durationDays}-Day {plan.targetCompany} SDE Plan
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                  <span>Daily hours: {plan.dailyHours}</span>
                  <span>Difficulty: {plan.difficultyPreference}</span>
                  <span>Completed: {totals.completed}/{totals.total}</span>
                  {plan.nextDayToResume ? <span>Resume from Day {plan.nextDayToResume}</span> : null}
                </div>
                <Progress value={totals.percent} />
                <p className="text-xs text-muted-foreground">Overall completion: {totals.percent}%</p>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {(plan.days || []).map((day) => (
                <Card key={day.planDayId} className="border-border/60 bg-card/20">
                  <CardHeader className="pb-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <CardTitle className="text-lg">
                        Day {day.day} - {day.focusTopic}
                      </CardTitle>
                      <span className="text-sm text-muted-foreground">
                        {day.completedProblems}/{day.totalProblems} done ({day.completionPercent}%)
                      </span>
                    </div>
                    <Progress value={day.completionPercent} />
                    {day.isMissed && (
                      <p className="text-xs text-amber-400">
                        Missed day detected. Suggested resume slot: Day {day.suggestedDay}
                      </p>
                    )}
                    {day.isMockInterviewDay && (
                      <p className="text-xs text-primary">Mock interview day</p>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {(day.problems || []).map((problem) => {
                      const updating = updatingProblemId === problem.planProblemId;
                      const checked = problem.status === 'completed';
                      const difficulty = problem.difficulty || 'medium';
                      return (
                        <div key={problem.planProblemId} className="flex items-center gap-3 rounded-lg border border-border/40 px-3 py-2">
                          <Checkbox
                            checked={checked}
                            disabled={updating}
                            onCheckedChange={(isChecked) => updateProblemStatus(problem.planProblemId, isChecked ? 'completed' : 'not_started')}
                          />
                          <Link to={`/problems/${problem.problemId}`} className="flex-1 hover:text-primary transition-colors">
                            {problem.title}
                          </Link>
                          <span className={`inline-flex min-w-[4.5rem] justify-center px-2 py-0.5 rounded-full text-xs font-medium border ${DIFFICULTY_BG?.[difficulty] ?? 'bg-muted border-border'} ${DIFFICULTY_COLORS?.[difficulty] ?? 'text-muted-foreground'}`}>
                            {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                          </span>
                          <button
                            type="button"
                            className="text-xs text-muted-foreground hover:text-foreground border border-border/50 rounded px-2 py-1"
                            disabled={updating}
                            onClick={() => updateProblemStatus(problem.planProblemId, nextStatus(problem.status))}
                            title="Cycle status"
                          >
                            {updating ? 'Saving...' : STATUS_LABEL[problem.status] || STATUS_LABEL.not_started}
                          </button>
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

