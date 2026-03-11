import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import IfElseIcon from '@/components/IfElseIcon';
import { LogOut, User, Filter, CheckCircle2, Circle, AlertCircle, Search, LayoutGrid, Shuffle, Trash2, HelpCircle, Star, ExternalLink, ChevronUp, ChevronDown, FileText } from 'lucide-react';
import { DIFFICULTY_COLORS, DIFFICULTY_BG } from '@/utils/constants';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

const STARRED_KEY = 'ifelse-starred-ids';

// Topic order for grouping: Array → array related problems, Hash Table → hashmap related, etc.
const TAG_ORDER = [
  'Array', 'Hash Table', 'Two Pointers', 'Sliding Window', 'Stack',
  'Binary Search', 'Linked List', 'Tree', 'Binary Tree', 'BST', 'Heap',
  'Backtracking', 'Trie', 'Graph', 'Dynamic Programming', 'Greedy',
  'Intervals', 'Math', 'Bit Manipulation', 'Recursion', 'Sorting', 'String',
  'Prefix Sum', 'Design', 'Matrix', 'Sieve', 'BFS', 'DFS', 'Topological Sort', 'Deque', 'Divide and Conquer'
];

const getStarredIds = () => {
  try {
    const raw = localStorage.getItem(STARRED_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

const diffOrder = (d) => (d === 'easy' ? 0 : d === 'medium' ? 1 : 2);

const ProblemsPage = () => {
  const [allProblems, setAllProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(null);
  const [meta, setMeta] = useState({ tags: [], companies: [] });
  const [filterOpen, setFilterOpen] = useState(false);
  const [difficulty, setDifficulty] = useState('all');
  const [status, setStatus] = useState('all');
  const [tag, setTag] = useState('all');
  const [company, setCompany] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [topicPanelExpanded, setTopicPanelExpanded] = useState(true);
  const [sortBy, setSortBy] = useState('title'); // 'title' | 'difficulty'
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' | 'desc'
  const [shuffledIds, setShuffledIds] = useState(null);
  const [starredIds, setStarredIds] = useState(() => new Set(getStarredIds()));
  const [assignedMap, setAssignedMap] = useState({});
  const [deletingProgress, setDeletingProgress] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);
  const { user, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();

  const handleDeleteAllProgress = async () => {
    setDeletingProgress(true);
    try {
      await api.delete('/user/progress');
      await fetchProgress();
      toast.success('All your progress and submissions have been deleted.');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete progress');
    } finally {
      setDeletingProgress(false);
    }
  };

  const fetchProblems = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (difficulty !== 'all') params.difficulty = difficulty;
      if (tag !== 'all') params.tag = tag;
      if (company !== 'all') params.company = company;
      const response = await api.get('/problems', { params });
      setAllProblems(response.data || []);
    } catch (error) {
      toast.error('Failed to load problems');
      setAllProblems([]);
    } finally {
      setLoading(false);
    }
  }, [difficulty, tag, company]);

  useEffect(() => {
    if (authLoading) return;
    fetchProblems();
    fetchMeta();
    if (user) {
      fetchProgress();
      fetchAssignedMap();
    } else {
      setAssignedMap({});
    }
  }, [user, authLoading, fetchProblems]);

  useEffect(() => {
    if (authLoading) return;
    fetchProblems();
  }, [difficulty, tag, company, authLoading, fetchProblems]);

  useEffect(() => {
    setShuffledIds(null);
  }, [difficulty, tag, company, status, searchQuery]);

  const fetchMeta = async () => {
    try {
      const res = await api.get('/problems/meta');
      const data = res.data || { tags: [], companies: [] };
      setMeta({ tags: data.tags || [], companies: data.companies || [] });
    } catch {
      setMeta({ tags: [], companies: [] });
    }
  };

  const fetchProgress = async () => {
    try {
      const res = await api.get('/user/progress');
      setProgress(res.data);
    } catch {
      setProgress(null);
    }
  };

  const fetchAssignedMap = async () => {
    try {
      const res = await api.get('coach/my-plan/assigned-map');
      setAssignedMap(res.data?.assigned || {});
    } catch {
      setAssignedMap({});
    }
  };

  const filteredByStatus = useCallback((list) => {
    if (!list || status === 'all') return list;
    const solved = new Set(progress?.solved_problem_ids || []);
    const attempted = new Set(progress?.attempted_problem_ids || []);
    if (status === 'solved') return list.filter((p) => solved.has(p.id));
    if (status === 'attempted') return list.filter((p) => attempted.has(p.id));
    if (status === 'not_started') return list.filter((p) => !solved.has(p.id) && !attempted.has(p.id));
    return list;
  }, [status, progress]);

  const problemsToShow = useMemo(() => {
    let list = filteredByStatus(allProblems);
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      list = list.filter((p) => (p.title || '').toLowerCase().includes(q));
    }
    if (list.length === 0) return [];
    const order =
      sortBy === 'title'
      ? [...list].sort((a, b) => (a.title || '').localeCompare(b.title || '', undefined, { sensitivity: 'base' }) * (sortOrder === 'asc' ? 1 : -1))
      : [...list].sort((a, b) => (diffOrder(a.difficulty) - diffOrder(b.difficulty)) * (sortOrder === 'asc' ? 1 : -1));
    if (shuffledIds && shuffledIds.length > 0) {
      const byId = new Map(order.map((p) => [p.id, p]));
      const out = [];
      for (const id of shuffledIds) {
        if (byId.has(id)) out.push(byId.get(id));
      }
      return out;
    }
    return order;
  }, [allProblems, searchQuery, sortBy, sortOrder, shuffledIds, filteredByStatus]);

  // Group by tag: "Array" → array related problems list, "Hash Table" → hashmap related, etc.
  const problemsByTag = useMemo(() => {
    const byTag = new Map();
    for (const p of problemsToShow) {
      const tags = p.tags || [];
      if (tags.length === 0) {
        const other = 'Other';
        if (!byTag.has(other)) byTag.set(other, []);
        byTag.get(other).push(p);
      } else {
        for (const t of tags) {
          if (!byTag.has(t)) byTag.set(t, []);
          if (!byTag.get(t).some((x) => x.id === p.id)) byTag.get(t).push(p);
        }
      }
    }
    const ordered = [];
    for (const tag of TAG_ORDER) {
      if (byTag.has(tag)) ordered.push({ tag, problems: byTag.get(tag) });
    }
    for (const [tag, probs] of byTag) {
      if (!TAG_ORDER.includes(tag)) ordered.push({ tag, problems: probs });
    }
    return ordered;
  }, [problemsToShow]);

  const toggleStar = (problemId) => {
    setStarredIds((prev) => {
      const next = prev.has(problemId) ? new Set([...prev].filter((id) => id !== problemId)) : new Set([...prev, problemId]);
      try {
        localStorage.setItem(STARRED_KEY, JSON.stringify([...next]));
      } catch {}
      return next;
    });
  };

  const handleSort = (field) => {
    if (sortBy === field) setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
    else {
      setSortBy(field);
      setSortOrder('asc');
    }
    setShuffledIds(null);
  };

  const handleShuffle = () => {
    let list = filteredByStatus(allProblems);
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      list = list.filter((p) => (p.title || '').toLowerCase().includes(q));
    }
    const ids = list.map((p) => p.id);
    for (let i = ids.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [ids[i], ids[j]] = [ids[j], ids[i]];
    }
    setShuffledIds(ids);
    toast.success('List shuffled');
  };

  const clearFilters = () => {
    setDifficulty('all');
    setStatus('all');
    setTag('all');
    setCompany('all');
    setSearchQuery('');
    setShuffledIds(null);
    setTopicPanelExpanded(true);
    toast.success('Filters cleared');
  };

  const hasActiveFilters = difficulty !== 'all' || status !== 'all' || tag !== 'all' || company !== 'all' || (searchQuery && searchQuery.trim()) || shuffledIds;

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

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
              <Link to="/dashboard" data-testid="nav-dashboard-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <User className="w-4 h-4 mr-2" />
                  {user?.username}
                </Button>
              </Link>
              <Link to="/coach" data-testid="nav-coach-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <IfElseIcon className="w-4 h-4 mr-2" />
                  If Else Coach
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
        <h1 className="font-heading font-bold text-4xl md:text-5xl mb-6">
          Practice Problems
        </h1>

        {/* Top bar: Search, Filter, Sort, Shuffle, Trash, Help */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <div className="relative flex-1 min-w-[200px] max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-card border-border"
            />
          </div>
          <Popover open={filterOpen} onOpenChange={setFilterOpen}>
            <PopoverTrigger asChild>
              <Button variant="outline" size="icon" className="shrink-0 border-border bg-card" title="Filters">
                <Filter className="w-4 h-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[380px] p-4 bg-card border-border" align="start">
              <p className="text-sm text-muted-foreground mb-4">Match <strong>all</strong> of the following filters:</p>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium w-24">Difficulty</span>
                  <Select value={difficulty} onValueChange={setDifficulty}>
                    <SelectTrigger className="flex-1 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any</SelectItem>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium w-24">Status</span>
                  <Select value={status} onValueChange={setStatus}>
                    <SelectTrigger className="flex-1 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any</SelectItem>
                      <SelectItem value="solved">Solved</SelectItem>
                      <SelectItem value="attempted">Attempted</SelectItem>
                      <SelectItem value="not_started">Not started</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium w-24">Topic</span>
                  <Select value={tag} onValueChange={setTag}>
                    <SelectTrigger className="flex-1 bg-background">
                      <SelectValue placeholder="Select..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any</SelectItem>
                      {(meta.tags || []).map((t) => (
                        <SelectItem key={typeof t === 'object' ? t.name : t} value={typeof t === 'object' ? t.name : t}>
                          {typeof t === 'object' ? `${t.name} (${t.count})` : t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium w-24">Company</span>
                  <Select value={company} onValueChange={setCompany}>
                    <SelectTrigger className="flex-1 bg-background">
                      <SelectValue placeholder="Select..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any</SelectItem>
                      {(meta.companies || []).map((c) => (
                        <SelectItem key={typeof c === 'object' ? c.name : c} value={typeof c === 'object' ? c.name : c}>
                          {typeof c === 'object' ? `${c.name} (${c.count})` : c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button className="w-full mt-4" onClick={() => setFilterOpen(false)}>Apply</Button>
            </PopoverContent>
          </Popover>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="icon" className="shrink-0 border-border" title="Sort">
                <LayoutGrid className="w-4 h-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-48 p-2" align="start">
              <button
                type="button"
                className="w-full px-3 py-2 text-left text-sm rounded hover:bg-muted/50 flex items-center justify-between"
                onClick={() => handleSort('title')}
              >
                Problem {sortBy === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                type="button"
                className="w-full px-3 py-2 text-left text-sm rounded hover:bg-muted/50 flex items-center justify-between"
                onClick={() => handleSort('difficulty')}
              >
                Difficulty {sortBy === 'difficulty' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
            </PopoverContent>
          </Popover>
          <Button variant="outline" size="icon" className="shrink-0 border-border" title="Shuffle" onClick={handleShuffle}>
            <Shuffle className="w-4 h-4" />
          </Button>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" className="shrink-0 text-muted-foreground" onClick={clearFilters}>
              Clear filters
            </Button>
          )}
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="icon" className="shrink-0 border-border border-destructive/50 text-destructive hover:bg-destructive/10" title="Delete all progress">
                <Trash2 className="w-4 h-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete all your progress?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete all your submissions and reset your solved/attempted progress. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteAllProgress}
                  disabled={deletingProgress}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  {deletingProgress ? 'Deleting...' : 'Delete all'}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground" title="About" onClick={() => setAboutOpen(true)}>
            <HelpCircle className="w-4 h-4" />
          </Button>
        </div>

        {/* About modal */}
        <Dialog open={aboutOpen} onOpenChange={setAboutOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-card border-border">
            <DialogHeader>
              <DialogTitle className="text-center text-2xl font-bold">About</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 text-sm text-muted-foreground">
              <p className="text-foreground">
                Hi, we created If Else to make coding interview prep easier!
              </p>
              <ul className="list-disc list-inside space-y-2 pl-2">
                <li>We offer a <strong className="text-foreground">curated list</strong> of algorithm &amp; data structure problems, beginner-friendly and organized by topic.</li>
                <li>Each problem includes <strong className="text-foreground">multiple solution approaches</strong> (e.g. brute force, optimal) with code in Python, JavaScript, Java, C++, and C.</li>
                <li>Use built-in <strong className="text-foreground">hints and solutions</strong> when you need a nudge or want to compare your approach.</li>
                <li>Get stuck? Use <strong className="text-foreground">If Else AI</strong> for progressive hints, code review, and debug help—without giving away the answer.</li>
              </ul>
              <p>See below for more details.</p>
              <div className="rounded-lg overflow-hidden border border-border/50 bg-muted/20">
                <iframe
                  title="How to Get Good at Algorithms & Data Structures"
                  className="w-full aspect-video"
                  src="https://www.youtube.com/embed/7U4nLbPe82M"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            </div>
            <DialogFooter className="flex justify-center sm:justify-center">
              <Button onClick={() => setAboutOpen(false)} variant="secondary">
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Topic chips panel (expandable) */}
        <div className="mb-4">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-sm text-muted-foreground">Topics</span>
            <Button variant="ghost" size="sm" className="text-muted-foreground" onClick={() => setTopicPanelExpanded(!topicPanelExpanded)}>
              {topicPanelExpanded ? 'Collapse' : 'Expand'}
              {topicPanelExpanded ? <ChevronUp className="w-4 h-4 ml-1 inline" /> : <ChevronDown className="w-4 h-4 ml-1 inline" />}
            </Button>
          </div>
          {topicPanelExpanded && (
            <div className="flex flex-wrap gap-2">
              {(meta.tags || []).map((t) => {
                const name = typeof t === 'object' ? t.name : t;
                const count = typeof t === 'object' ? t.count : (allProblems.filter((p) => (p.tags || []).includes(name)).length);
                const active = tag === name;
                return (
                  <button
                    key={name}
                    type="button"
                    onClick={() => setTag(active ? 'all' : name)}
                    className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${active ? 'bg-primary text-primary-foreground border-primary' : 'bg-card border-border hover:bg-muted/50'}`}
                  >
                    {name} {count}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading problems...</p>
          </div>
        ) : problemsToShow.length === 0 ? (
          <div className="text-center py-12">
            {allProblems.length === 0 ? (
              <>
                <p className="text-muted-foreground font-medium">No problems available</p>
                <p className="text-muted-foreground text-sm mt-1">The problem list is empty. If you run the app locally, seed the database (e.g. run the backend seed script).</p>
              </>
            ) : (
              <p className="text-muted-foreground">No problems match your filters</p>
            )}
          </div>
        ) : tag !== 'all' ? (
          <div className="space-y-4" data-testid="problems-list">
            <h2 className="font-heading font-semibold text-xl text-foreground">{tag}</h2>
            <div className="bg-card border border-border/50 rounded-lg overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/30 border-b border-border">
                    <tr>
                      <th className="px-3 py-3 text-left text-sm font-heading font-semibold w-10">Status</th>
                      <th className="px-3 py-3 text-left text-sm font-heading font-semibold w-10">Star</th>
                      <th className="px-4 py-3 text-left text-sm font-heading font-semibold">
                        <button type="button" className="inline-flex items-center gap-1 hover:text-foreground" onClick={() => handleSort('title')}>
                          Problem
                          {sortBy === 'title' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
                        </button>
                      </th>
                      <th className="px-4 py-3 text-center text-sm font-heading font-semibold w-28">
                        <button type="button" className="inline-flex items-center justify-center gap-1 w-full hover:text-foreground" onClick={() => handleSort('difficulty')}>
                          Difficulty
                          {sortBy === 'difficulty' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
                        </button>
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-heading font-semibold w-24">Acceptance</th>
                      <th className="px-4 py-3 text-left text-sm font-heading font-semibold w-20">Solution</th>
                    </tr>
                  </thead>
                  <tbody>
                    {problemsToShow.map((problem) => {
                      const solvedSet = new Set(progress?.solved_problem_ids || []);
                      const attemptedSet = new Set(progress?.attempted_problem_ids || []);
                      const isSolved = solvedSet.has(problem.id);
                      const isAttempted = attemptedSet.has(problem.id);
                      const isStarred = starredIds.has(problem.id);
                      const assigned = assignedMap?.[problem.id];
                      return (
                        <tr
                          key={problem.id}
                          className="border-b border-border/30 hover:bg-muted/20 transition-colors"
                          data-testid={`problem-row-${problem.id}`}
                        >
                          <td className="px-3 py-3">
                            {isSolved ? (
                              <CheckCircle2 className="w-5 h-5 text-green-500" title="Solved" />
                            ) : isAttempted ? (
                              <AlertCircle className="w-5 h-5 text-amber-500" title="Attempted" />
                            ) : (
                              <Circle className="w-5 h-5 text-muted-foreground" title="Not started" />
                            )}
                          </td>
                          <td className="px-3 py-3">
                            <button type="button" onClick={() => toggleStar(problem.id)} className="text-muted-foreground hover:text-foreground" title={isStarred ? 'Unstar' : 'Star'}>
                              <Star className={`w-5 h-5 ${isStarred ? 'fill-amber-400 text-amber-400' : ''}`} />
                            </button>
                          </td>
                          <td className="px-4 py-3">
                            <Link
                              to={`/problems/${problem.id}`}
                              className="font-medium hover:text-primary transition-colors inline-flex items-center gap-1"
                              data-testid={`problem-title-${problem.id}`}
                            >
                              {problem.title}
                              <ExternalLink className="w-3.5 h-3.5 opacity-70" />
                            </Link>
                            {assigned ? (
                              <span className="ml-2 inline-flex items-center rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-[11px] text-primary">
                                Day {assigned.day}
                              </span>
                            ) : null}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span
                              className={`inline-flex min-w-[4.5rem] justify-center px-3 py-1 rounded-full text-sm font-medium border ${DIFFICULTY_BG?.[problem.difficulty] ?? 'bg-muted border-border'} ${DIFFICULTY_COLORS?.[problem.difficulty] ?? 'text-muted-foreground'}`}
                            >
                              {(problem.difficulty ?? 'N/A').charAt(0).toUpperCase() + (problem.difficulty ?? '').slice(1)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {(problem.total_submissions ?? 0) > 0 ? `${(problem.acceptance_rate ?? 0).toFixed(1)}%` : '-'}
                          </td>
                          <td className="px-4 py-3">
                            <Link to={`/problems/${problem.id}`} className="text-muted-foreground hover:text-foreground" title="View solution">
                              <FileText className="w-5 h-5" />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-10" data-testid="problems-list">
            {problemsByTag.map(({ tag: sectionTag, problems }) => (
              <div key={sectionTag}>
                <h2 className="font-heading font-semibold text-xl mb-3 text-foreground">{sectionTag}</h2>
                <div className="bg-card border border-border/50 rounded-lg overflow-hidden shadow-xl">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-muted/30 border-b border-border">
                        <tr>
                          <th className="px-3 py-3 text-left text-sm font-heading font-semibold w-10">Status</th>
                          <th className="px-3 py-3 text-left text-sm font-heading font-semibold w-10">Star</th>
                          <th className="px-4 py-3 text-left text-sm font-heading font-semibold">
                            <button type="button" className="inline-flex items-center gap-1 hover:text-foreground" onClick={() => handleSort('title')}>
                              Problem
                              {sortBy === 'title' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
                            </button>
                          </th>
                          <th className="px-4 py-3 text-center text-sm font-heading font-semibold w-28">
                            <button type="button" className="inline-flex items-center justify-center gap-1 w-full hover:text-foreground" onClick={() => handleSort('difficulty')}>
                              Difficulty
                              {sortBy === 'difficulty' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
                            </button>
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-heading font-semibold w-24">Acceptance</th>
                          <th className="px-4 py-3 text-left text-sm font-heading font-semibold w-20">Solution</th>
                        </tr>
                      </thead>
                      <tbody>
                        {problems.map((problem) => {
                          const solvedSet = new Set(progress?.solved_problem_ids || []);
                          const attemptedSet = new Set(progress?.attempted_problem_ids || []);
                          const isSolved = solvedSet.has(problem.id);
                          const isAttempted = attemptedSet.has(problem.id);
                          const isStarred = starredIds.has(problem.id);
                          const assigned = assignedMap?.[problem.id];
                          const diff = problem.difficulty ?? 'easy';
                          return (
                            <tr
                              key={problem.id}
                              className="border-b border-border/30 hover:bg-muted/20 transition-colors"
                              data-testid={`problem-row-${problem.id}`}
                            >
                              <td className="px-3 py-3">
                                {isSolved ? (
                                  <CheckCircle2 className="w-5 h-5 text-green-500" title="Solved" />
                                ) : isAttempted ? (
                                  <AlertCircle className="w-5 h-5 text-amber-500" title="Attempted" />
                                ) : (
                                  <Circle className="w-5 h-5 text-muted-foreground" title="Not started" />
                                )}
                              </td>
                              <td className="px-3 py-3">
                                <button type="button" onClick={() => toggleStar(problem.id)} className="text-muted-foreground hover:text-foreground" title={isStarred ? 'Unstar' : 'Star'}>
                                  <Star className={`w-5 h-5 ${isStarred ? 'fill-amber-400 text-amber-400' : ''}`} />
                                </button>
                              </td>
                              <td className="px-4 py-3">
                                <Link
                                  to={`/problems/${problem.id}`}
                                  className="font-medium hover:text-primary transition-colors inline-flex items-center gap-1"
                                  data-testid={`problem-title-${problem.id}`}
                                >
                                  {problem.title}
                                  <ExternalLink className="w-3.5 h-3.5 opacity-70" />
                                </Link>
                                {assigned ? (
                                  <span className="ml-2 inline-flex items-center rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-[11px] text-primary">
                                    Day {assigned.day}
                                  </span>
                                ) : null}
                              </td>
                              <td className="px-4 py-3 text-center">
                                <span
                                  className={`inline-flex min-w-[4.5rem] justify-center px-3 py-1 rounded-full text-sm font-medium border ${DIFFICULTY_BG?.[diff] ?? 'bg-muted border-border'} ${DIFFICULTY_COLORS?.[diff] ?? 'text-muted-foreground'}`}
                                >
                                  {diff.charAt(0).toUpperCase() + diff.slice(1)}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-sm text-muted-foreground">
                                {(problem.total_submissions ?? 0) > 0 ? `${(problem.acceptance_rate ?? 0).toFixed(1)}%` : '-'}
                              </td>
                              <td className="px-4 py-3">
                                <Link to={`/problems/${problem.id}`} className="text-muted-foreground hover:text-foreground" title="View solution">
                                  <FileText className="w-5 h-5" />
                                </Link>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProblemsPage;
