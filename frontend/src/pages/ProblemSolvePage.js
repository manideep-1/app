import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Play, Check, X, ArrowLeft, Timer, Lightbulb, Building2, Tag, ChevronDown, ChevronUp, Beaker, ArrowRight } from 'lucide-react';
import IfElseIcon from '@/components/IfElseIcon';
import { DIFFICULTY_COLORS, DIFFICULTY_BG, STATUS_COLORS } from '@/utils/constants';
import { toast } from 'sonner';
import Editor from '@monaco-editor/react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, Copy } from 'lucide-react';
import AICoachPanel from '@/components/AICoachPanel';

/** Normalize code block indentation for display: strip common leading spaces so relative indent is preserved. */
function normalizeCodeIndent(code) {
  if (code == null || typeof code !== 'string') return code;
  const lines = code.split(/\r?\n/);
  let minIndent = Infinity;
  for (const line of lines) {
    if (line.trim().length === 0) continue;
    const m = line.match(/^(\s*)/);
    const len = m ? m[1].length : 0;
    minIndent = Math.min(minIndent, len);
  }
  if (minIndent === 0 || minIndent === Infinity) return code;
  return lines.map((line) => (line.length >= minIndent ? line.slice(minIndent) : line)).join('\n');
}

/** Derive a problem-appropriate function name from title (e.g. "Two Sum" -> twoSum, "Contains Duplicate" -> containsDuplicate). */
function titleToFunctionName(title) {
  if (!title || typeof title !== 'string') return 'solution';
  const numberWord = { 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine' };
  const words = title.trim().split(/\s+/).map((w) => w.replace(/[^a-zA-Z0-9]/g, '')).filter(Boolean);
  if (words.length === 0) return 'solution';
  const first = words[0];
  const firstChar = first.charAt(0);
  let lead = first;
  if (/^\d$/.test(firstChar) && numberWord[firstChar]) {
    lead = numberWord[firstChar] + first.slice(1);
  } else {
    lead = firstChar.toLowerCase() + first.slice(1);
  }
  const rest = words.slice(1).map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');
  return lead + rest;
}

const ProblemSolvePage = () => {
  const { problemId } = useParams();
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submitting, setSubmitting] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submissions, setSubmissions] = useState([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [expandedSubmissionId, setExpandedSubmissionId] = useState(null);
  const [submissionFilterStatus, setSubmissionFilterStatus] = useState('');
  const [submissionFilterLanguage, setSubmissionFilterLanguage] = useState('');
  // NeetCode-style: timer/stopwatch
  const [timerOpen, setTimerOpen] = useState(false);
  const [timerMode, setTimerMode] = useState('stopwatch'); // 'stopwatch' | 'timer'
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [timerRunning, setTimerRunning] = useState(false);
  const timerIntervalRef = useRef(null);
  // Cursor position in editor
  const [cursorPos, setCursorPos] = useState({ line: 1, column: 1 });
  const editorRef = useRef(null);
  // Solution tabs (multiple buffers)
  const [solutionTabs, setSolutionTabs] = useState([{ id: 1, name: 'Solution 1' }]);
  const [activeSolutionIndex, setActiveSolutionIndex] = useState(0);
  // Bottom: Test Case vs Output; which test case selected
  const [bottomTab, setBottomTab] = useState('testcase'); // 'testcase' | 'output'
  const [activeTestCaseIndex, setActiveTestCaseIndex] = useState(0);
  // Hints & Console open; progressive hints (LeetCode-style: reveal one by one)
  const [hintsOpen, setHintsOpen] = useState(false);
  const [hintsRevealedCount, setHintsRevealedCount] = useState(0);
  const [consoleOpen, setConsoleOpen] = useState(false);
  // User-added manual test cases
  const [customTestCases, setCustomTestCases] = useState([]);
  const [newTestInput, setNewTestInput] = useState('');
  const [relatedProblems, setRelatedProblems] = useState([]);
  const [solutionCodeOpen, setSolutionCodeOpen] = useState({}); // approach index -> open (default true)
  const [solutionCodeLang, setSolutionCodeLang] = useState('python'); // language for solution code tabs: python | javascript | java | cpp | c

  const [aiPanelOpen, setAiPanelOpen] = useState(false);

  /** Which language runtimes are available on the server (from GET /api/runtimes). null = loading. */
  const [runtimes, setRuntimes] = useState(null);

  const draftSaveTimeoutRef = useRef(null);
  const DRAFT_KEY = (id) => `ifelse_draft_${id}`;

  const loadDraft = (pid) => {
    try {
      const raw = localStorage.getItem(DRAFT_KEY(pid));
      if (!raw) return null;
      const data = JSON.parse(raw);
      if (data && typeof data.code === 'string') return data;
    } catch (_) { /* ignore */ }
    return null;
  };

  const saveDraft = (pid, codeVal, langVal, tabsVal) => {
    if (!pid) return;
    try {
      const payload = {
        code: codeVal ?? '',
        language: langVal ?? 'python',
        solutionTabs: (tabsVal || []).map((t) => ({ id: t.id, name: t.name, code: t.code ?? '' })),
      };
      localStorage.setItem(DRAFT_KEY(pid), JSON.stringify(payload));
    } catch (_) { /* ignore */ }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProblem();
    setSolutionCodeOpen({});
  }, [problemId, user, authLoading]);

  // Fetch which runtimes are available on the server (so we only offer runnable languages)
  useEffect(() => {
    api.get('/runtimes')
      .then((res) => setRuntimes(res.data || {}))
      .catch(() => setRuntimes({}));
  }, []);

  // If current language is not available on server, switch to first available
  const editorLanguageOrder = ['python', 'javascript', 'java', 'cpp', 'c'];
  const availableEditorLanguages =
    runtimes && Object.keys(runtimes).length > 0
      ? (() => {
          const available = editorLanguageOrder.filter((lang) => runtimes[lang] === true);
          return available.length > 0 ? available : editorLanguageOrder;
        })()
      : editorLanguageOrder;
  useEffect(() => {
    if (!runtimes || typeof runtimes !== 'object') return;
    const available = editorLanguageOrder.filter((lang) => runtimes[lang] === true);
    const list = available.length > 0 ? available : editorLanguageOrder;
    if (list.length > 0 && !list.includes(language)) {
      setLanguage(list[0]);
    }
  }, [runtimes, language]);

  useEffect(() => {
    if (problemId && user) fetchSubmissions();
  }, [problemId, user, submissionFilterStatus, submissionFilterLanguage]);

  // Persist code draft to localStorage (debounced) so refresh keeps the code
  useEffect(() => {
    if (!problemId || !problem) return;
    if (draftSaveTimeoutRef.current) clearTimeout(draftSaveTimeoutRef.current);
    draftSaveTimeoutRef.current = setTimeout(() => {
      saveDraft(problemId, code, language, solutionTabs);
      draftSaveTimeoutRef.current = null;
    }, 500);
    return () => {
      if (draftSaveTimeoutRef.current) clearTimeout(draftSaveTimeoutRef.current);
    };
  }, [problemId, problem, code, language, solutionTabs]);

  // Timer/Stopwatch tick
  useEffect(() => {
    if (!timerRunning) return;
    timerIntervalRef.current = setInterval(() => {
      setTimerSeconds((s) => {
        if (timerMode === 'timer') {
          if (s <= 0) {
            if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
            return 0;
          }
          return s - 1;
        }
        return s + 1;
      });
    }, 1000);
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [timerRunning, timerMode]);

  const fetchSubmissions = async () => {
    if (!problemId) return;
    setSubmissionsLoading(true);
    try {
      const params = { problem_id: problemId };
      if (submissionFilterStatus) params.status = submissionFilterStatus;
      if (submissionFilterLanguage) params.language = submissionFilterLanguage;
      const res = await api.get('/submissions', { params });
      setSubmissions(res.data || []);
    } catch {
      setSubmissions([]);
    } finally {
      setSubmissionsLoading(false);
    }
  };

  const fetchProblem = async () => {
    try {
      setHintsRevealedCount(0);
      const response = await api.get(`/problems/${problemId}`);
      const p = response.data;
      setProblem(p);
      try {
        const rel = await api.get(`/problems/${problemId}/related`);
        setRelatedProblems(rel.data || []);
      } catch {
        setRelatedProblems([]);
      }
      // LeetCode-style: user writes only the solution function; driver (server-side) handles input/output
      const fnName = titleToFunctionName(p.title);
      const starters = {
        python: p.starter_code_python || `def ${fnName}(nums):\n    # Implement the solution function only. Do not read input.\n    pass\n`,
        javascript: p.starter_code_javascript || `function ${fnName}(nums) {\n    // Implement the solution function only. Do not read input.\n}\n`,
        java: p.starter_code_java || `// Only implement the solution. Do not read input - the system calls your method with test inputs.\npublic class Solution {\n    public static int ${fnName}(int[] nums) {\n        return 0;\n    }\n}\n`,
        cpp: p.starter_code_cpp || `// Only implement the solution. Do not read input - the system calls your function.\nclass Solution {\npublic:\n    int ${fnName}(vector<int>& nums) {\n        return 0;\n    }\n};\n`,
        c: p.starter_code_c || `// Only implement the solution. Do not read input - the system calls your function.\nint ${fnName}(int* nums, int n) {\n    return 0;\n}\n`,
      };
      const draft = loadDraft(problemId);
      if (draft && draft.code) {
        setLanguage(draft.language || language);
        setCode(draft.code);
        const tabs = Array.isArray(draft.solutionTabs) && draft.solutionTabs.length > 0
          ? draft.solutionTabs.map((t, i) => ({ id: t.id || i + 1, name: t.name || `Solution ${i + 1}`, code: t.code ?? '' }))
          : [{ id: 1, name: 'Solution 1', code: draft.code }];
        setSolutionTabs(tabs);
        setActiveSolutionIndex(0);
      } else {
        const starter = starters[language] || starters.python;
        setCode(starter);
        setSolutionTabs([{ id: 1, name: 'Solution 1', code: starter }]);
        setActiveSolutionIndex(0);
      }
    } catch (error) {
      toast.error('Failed to load problem');
      navigate('/problems');
    } finally {
      setLoading(false);
    }
  };

  const getStarterCode = (lang) => {
    if (!problem) return '';
    const fnName = titleToFunctionName(problem.title);
    // Function-only: user implements the solution; system handles input/output via driver
    const starters = {
      python: problem.starter_code_python || `def ${fnName}(nums):\n    # Implement only the solution function. Do not read input.\n    pass\n`,
      javascript: problem.starter_code_javascript || `function ${fnName}(nums) {\n    // Implement only the solution function. Do not read input.\n}\n`,
      java: problem.starter_code_java || `// Implement only the solution. Input is provided by the system.\npublic class Solution {\n    public static int ${fnName}(int[] nums) { return 0; }\n}\n`,
      cpp: problem.starter_code_cpp || `// Implement only the solution. Input is provided by the system.\nclass Solution {\npublic:\n    int ${fnName}(vector<int>& nums) { return 0; }\n};\n`,
      c: problem.starter_code_c || `// Implement only the solution. Input is provided by the system.\nint ${fnName}(int* nums, int n) { return 0; }\n`,
    };
    return starters[lang] || starters.python;
  };

  const setCurrentCode = (value) => {
    setSolutionTabs((prev) => {
      const next = [...prev];
      if (next[activeSolutionIndex]) next[activeSolutionIndex] = { ...next[activeSolutionIndex], code: value ?? '' };
      return next;
    });
    setCode(value ?? '');
  };

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    if (problem) {
      const starter = getStarterCode(newLanguage);
      setSolutionTabs((prev) => {
        const next = [...prev];
        if (next[activeSolutionIndex]) next[activeSolutionIndex] = { ...next[activeSolutionIndex], code: starter };
        return next;
      });
      setCode(starter);
    }
  };

  const addSolutionTab = () => {
    const newTab = { id: Date.now(), name: `Solution ${solutionTabs.length + 1}`, code: getStarterCode(language) };
    setSolutionTabs((prev) => [...prev, newTab]);
    const nextIndex = solutionTabs.length;
    setActiveSolutionIndex(nextIndex);
    setCode(newTab.code);
  };

  const removeSolutionTab = (indexToRemove, e) => {
    e?.stopPropagation();
    if (solutionTabs.length <= 1) return;
    const next = solutionTabs.filter((_, i) => i !== indexToRemove);
    const newActive = activeSolutionIndex >= next.length ? Math.max(0, next.length - 1)
      : (activeSolutionIndex > indexToRemove ? activeSolutionIndex - 1 : activeSolutionIndex);
    setSolutionTabs(next);
    setActiveSolutionIndex(newActive);
    setCode(next[newActive]?.code ?? '');
  };

  const switchSolutionTab = (index) => {
    if (index === activeSolutionIndex) return;
    setSolutionTabs((prev) => {
      const next = [...prev];
      if (next[activeSolutionIndex]) next[activeSolutionIndex] = { ...next[activeSolutionIndex], code: code };
      return next;
    });
    setActiveSolutionIndex(index);
    setCode(solutionTabs[index]?.code ?? '');
  };

  const handleRun = async () => {
    if (!code.trim()) {
      toast.error('Please write some code first');
      return;
    }
    setRunning(true);
    setResult(null);
    try {
      const payload = { problem_id: problemId, code, language };
      if (customTestCases.length > 0) {
        payload.custom_test_cases = customTestCases.map(({ input }) => ({ input }));
      }
      const res = await api.post('/run', payload);
      setResult({
        status: res.data.status,
        result: {
          passed: res.data.passed,
          total: res.data.total,
          test_results: res.data.test_results || [],
          runtime: res.data.runtime,
          memory: res.data.memory,
        },
      });
      setBottomTab('output');
      if (res.data.status === 'accepted') {
        toast.success('All sample tests passed. Submit to run against hidden test cases.');
      } else {
        toast.error('Some tests failed. Check the Output tab for expected vs your output.');
      }
    } catch (error) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;
      if (status === 429) toast.error(detail || 'Too many requests. Please wait a moment before running again.');
      else toast.error(typeof detail === 'string' ? detail : 'Run failed');
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) {
      toast.error('Please write some code first');
      return;
    }
    setSubmitting(true);
    setResult(null);
    try {
      const response = await api.post('/submissions', {
        problem_id: problemId,
        code,
        language,
      });
      setResult(response.data);
      fetchSubmissions();
      setBottomTab('output');
      if (response.data.status === 'accepted') {
        toast.success('Accepted! All test cases passed. Great job.');
      } else {
        const statusMsg = response.data.status === 'wrong_answer' ? 'Wrong answer — check the test case breakdown below.' : response.data.status === 'time_limit_exceeded' ? 'Time limit exceeded — try a more efficient approach.' : response.data.status === 'runtime_error' ? 'Runtime error — check the output for details.' : 'Some test cases failed. Review the breakdown below.';
        toast.error(statusMsg);
      }
    } catch (error) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;
      if (status === 429) toast.error(detail || 'Too many submissions. Please wait a moment before submitting again.');
      else toast.error(typeof detail === 'string' ? detail : Array.isArray(detail) ? 'Validation error' : 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">{authLoading ? 'Loading...' : 'Loading problem...'}</p>
      </div>
    );
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b border-border/50 bg-card/30 px-6 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/problems" data-testid="back-to-problems-btn">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Problems
            </Button>
          </Link>
          <div className="h-6 w-px bg-border"></div>
          <h1 className="font-heading font-semibold text-xl" data-testid="problem-title">
            {problem?.title}
          </h1>
          <span
            className={`text-sm font-medium ${DIFFICULTY_COLORS[problem?.difficulty]}`}
          >
            {problem?.difficulty?.charAt(0).toUpperCase() + problem?.difficulty?.slice(1)}
          </span>
          {(problem?.total_submissions ?? 0) > 0 && (
            <span className="text-xs text-muted-foreground">
              {(problem?.acceptance_rate ?? 0).toFixed(1)}% acceptance
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Popover open={timerOpen} onOpenChange={setTimerOpen}>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full" title="Timer / Stopwatch">
                <Timer className="w-4 h-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-56 p-4" align="end">
              <p className="text-sm font-medium mb-3">MODE</p>
              <div className="flex gap-2 mb-4">
                <Button
                  size="sm"
                  variant={timerMode === 'stopwatch' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => { setTimerMode('stopwatch'); setTimerSeconds(0); }}
                >
                  Stopwatch
                </Button>
                <Button
                  size="sm"
                  variant={timerMode === 'timer' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => { setTimerMode('timer'); setTimerSeconds(45 * 60); }}
                >
                  Timer
                </Button>
              </div>
              <div className="text-2xl font-mono text-center mb-4">
                {Math.floor(timerSeconds / 60)
                  .toString()
                  .padStart(2, '0')}
                :{(timerSeconds % 60).toString().padStart(2, '0')}
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="flex-1 bg-green-600 hover:bg-green-700"
                  onClick={() => setTimerRunning(!timerRunning)}
                >
                  {timerRunning ? 'Pause' : 'Start'}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={() => { setTimerRunning(false); setTimerSeconds(timerMode === 'timer' ? 45 * 60 : 0); }}
                >
                  Reset
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {/* Main Content - AI panel opens only when user clicks Hint or If else AI */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        <PanelGroup key={aiPanelOpen ? 'three-panels' : 'two-panels'} direction="horizontal" className="w-full">
          <Panel defaultSize={aiPanelOpen ? 33.33 : 40} minSize={20} maxSize={50} className="flex flex-col min-w-0">
            {/* Left Panel - Problem Description (Question / Solution / Submissions) */}
            <div className="flex-1 overflow-y-auto flex flex-col border-r border-border/50" data-testid="problem-description">
          <Tabs defaultValue="question" className="w-full flex flex-col flex-1 min-h-0 p-6" onValueChange={(v) => v === 'submissions' && fetchSubmissions()}>
            <TabsList className="grid w-full grid-cols-3 bg-muted/30 shrink-0">
              <TabsTrigger value="question">Question</TabsTrigger>
              <TabsTrigger value="solution">Solution</TabsTrigger>
              <TabsTrigger value="submissions">Submissions</TabsTrigger>
            </TabsList>

            <TabsContent value="question" className="space-y-6 flex-1">
              {/* Topics & Company - pill row */}
              <div className="flex flex-wrap items-center gap-2">
                {problem?.tags && problem.tags.length > 0 && (
                  <div className="flex items-center gap-1.5">
                    <Tag className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Topics:</span>
                    {problem.tags.map((t) => (
                      <span key={t} className="text-sm px-2.5 py-0.5 bg-accent/10 text-accent rounded">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                {problem?.companies && problem.companies.length > 0 && (
                  <div className="flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Company:</span>
                    {problem.companies.map((c) => (
                      <span key={c} className="text-sm px-2.5 py-0.5 bg-secondary/10 text-secondary rounded">
                        {c}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Hints - own row, next line */}
              <div className="rounded-lg border border-border/50 bg-card/30 overflow-hidden">
                <Collapsible open={hintsOpen} onOpenChange={setHintsOpen}>
                  <CollapsibleTrigger asChild>
                    <button
                      type="button"
                      className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-muted/20 transition-colors"
                    >
                      <span className="flex items-center gap-2 font-medium text-foreground">
                        <Lightbulb className="w-4 h-4 text-primary" />
                        Hints
                        {problem?.hints?.length > 0 && (
                          <span className="text-sm font-normal text-muted-foreground">
                            ({hintsRevealedCount}/{problem.hints.length} revealed)
                          </span>
                        )}
                      </span>
                      {hintsOpen ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                    </button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="border-t border-border/50 px-4 py-4 space-y-4 bg-muted/5">
                      {problem?.hints && problem.hints.length > 0 ? (
                        <>
                          <ul className="space-y-3 list-none pl-0">
                            {problem.hints.slice(0, hintsRevealedCount).map((hint, i) => (
                              <li key={i} className="flex gap-3 items-start">
                                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary text-xs font-semibold mt-0.5">
                                  {i + 1}
                                </span>
                                <p className="text-sm text-foreground leading-relaxed flex-1">{hint}</p>
                              </li>
                            ))}
                          </ul>
                          {hintsRevealedCount < problem.hints.length ? (
                            <div className="mt-6 pt-4 border-t border-border/30">
                              <Button
                                variant="outline"
                                size="sm"
                                className="gap-2 border-border text-foreground hover:bg-muted/30"
                                onClick={() => setHintsRevealedCount((c) => Math.min(c + 1, problem.hints.length))}
                              >
                                <Lightbulb className="w-4 h-4 text-primary" />
                                Show Hint {hintsRevealedCount + 1}
                              </Button>
                            </div>
                          ) : (
                            <p className="text-xs text-muted-foreground pt-1 mt-6 border-t border-border/30">All hints revealed.</p>
                          )}
                        </>
                      ) : (
                        <p className="text-sm text-muted-foreground">No hints available for this problem.</p>
                      )}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </div>

              <div>
                <h2 className="font-heading font-semibold text-lg mb-2">Description</h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-muted-foreground whitespace-pre-wrap text-sm">{problem?.description}</p>
                </div>
              </div>

              {/* Examples (from visible test cases) */}
              <div>
                <h3 className="font-heading font-medium text-base mb-2">Examples</h3>
                <div className="space-y-4">
                  {(problem?.test_cases ?? [])
                    .filter((tc) => !tc.is_hidden)
                    .slice(0, 3)
                    .map((testCase, idx) => (
                      <div key={idx} className="bg-muted/20 rounded-lg p-4 border border-border/30">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Example {idx + 1}:</p>
                        <div className="mb-2">
                          <span className="text-xs text-muted-foreground">Input: </span>
                          <pre className="mt-0.5 text-sm font-mono bg-background/50 p-2 rounded overflow-x-auto">
                            {testCase.input}
                          </pre>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">Output: </span>
                          <pre className="mt-0.5 text-sm font-mono bg-background/50 p-2 rounded overflow-x-auto">
                            {testCase.expected_output}
                          </pre>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {problem?.test_cases?.some((tc) => tc.is_hidden) && (
                <p className="text-sm text-muted-foreground">
                  Additional hidden test cases run on Submit.
                </p>
              )}
              {problem?.constraints && (
                <div>
                  <h3 className="font-heading font-medium text-base mb-2">Constraints</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">{problem.constraints}</p>
                </div>
              )}
              {relatedProblems.length > 0 && (
                <div>
                  <h3 className="font-heading font-medium text-base mb-3">Related problems</h3>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {relatedProblems.map((rp) => (
                      <Link
                        key={rp.id}
                        to={`/problems/${rp.id}`}
                        className="flex items-center justify-between gap-3 rounded-lg border border-border/50 bg-card/50 px-4 py-3 text-left transition-colors hover:border-primary/40 hover:bg-muted/30"
                      >
                        <span className="font-medium text-sm truncate">{rp.title}</span>
                        <span
                          className={`shrink-0 inline-flex items-center justify-center min-w-[4.5rem] px-2.5 py-0.5 rounded-full text-xs font-medium border ${DIFFICULTY_BG[rp.difficulty] || 'bg-muted/50 border-border'} ${DIFFICULTY_COLORS[rp.difficulty] || 'text-muted-foreground'}`}
                        >
                          {rp.difficulty?.charAt(0).toUpperCase() + (rp.difficulty?.slice(1) ?? '')}
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="solution" className="mt-6 flex-1 min-h-0 data-[state=inactive]:hidden flex flex-col">
              <div className="flex-1 min-h-[200px] overflow-y-auto pb-6">
              {Array.isArray(problem?.solutions) && problem.solutions.length > 0 ? (
                <div className="space-y-8 pb-6">
                  {/* Topic / category subtitle (e.g. Stacks) */}
                  {problem?.tags?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium text-muted-foreground">Topic:</span>
                      {problem.tags.map((t) => (
                        <span key={t} className="text-sm px-2.5 py-1 bg-muted/50 text-foreground rounded-md border border-border/50">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Prerequisites */}
                  {problem.prerequisites && problem.prerequisites.length > 0 ? (
                    <div className="rounded-lg border border-border/50 bg-card/30 overflow-hidden">
                      <h3 className="px-4 py-3 border-b border-border/50 font-semibold text-base text-foreground">
                        Prerequisites
                      </h3>
                      <p className="px-4 pt-3 pb-1 text-sm text-muted-foreground">
                        Before attempting this problem, you should be comfortable with:
                      </p>
                      <ul className="list-disc list-inside px-4 pb-4 space-y-2 text-sm text-foreground leading-relaxed">
                        {problem.prerequisites.map((item, i) => (
                          <li key={i} className="text-muted-foreground">{item}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  {/* Solution approaches - same format for all */}
                  {problem.solutions.map((approach, idx) => (
                    <div key={idx} className="rounded-lg border border-border/50 bg-card/30 overflow-hidden">
                      <h3 className="px-4 py-3 border-b border-border/50 font-semibold text-base text-foreground">
                        {approach.title}
                      </h3>
                      <div className="p-4 space-y-5">
                        {approach.intuition != null && approach.intuition !== '' && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2">Intuition</h4>
                            <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{approach.intuition}</p>
                          </div>
                        )}
                        {approach.algorithm != null && approach.algorithm !== '' && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2">Algorithm</h4>
                            <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{approach.algorithm}</p>
                          </div>
                        )}
                        {(() => {
                          const codeByLang = {
                            python: approach.code_python || approach.code,
                            javascript: approach.code_javascript,
                            java: approach.code_java,
                            cpp: approach.code_cpp,
                            c: approach.code_c,
                          };
                          const availableLangs = ['python', 'javascript', 'java', 'cpp', 'c'].filter((l) => codeByLang[l]);
                          const displayCode = availableLangs.length ? (codeByLang[solutionCodeLang] || codeByLang.python) : null;
                          return displayCode != null && displayCode !== '' ? (
                            <div>
                              <Collapsible
                                open={solutionCodeOpen[idx] !== false}
                                onOpenChange={(open) => setSolutionCodeOpen((prev) => ({ ...prev, [idx]: open }))}
                              >
                                <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                                  <div className="flex items-center gap-2">
                                    <h4 className="text-sm font-semibold text-foreground">Code</h4>
                                    {availableLangs.length > 1 && (
                                      <Select value={solutionCodeLang} onValueChange={setSolutionCodeLang}>
                                        <SelectTrigger className="w-28 h-7 text-xs">
                                          <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                          {availableLangs.map((l) => (
                                            <SelectItem key={l} value={l}>
                                              {l === 'cpp' ? 'C++' : l === 'c' ? 'C' : l.charAt(0).toUpperCase() + l.slice(1)}
                                            </SelectItem>
                                          ))}
                                        </SelectContent>
                                      </Select>
                                    )}
                                  </div>
                                  <CollapsibleTrigger asChild>
                                    <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-8 gap-1 hover:text-foreground">
                                      {solutionCodeOpen[idx] !== false ? (
                                        <><ChevronDown className="w-3.5 h-3.5" /> Collapse</>
                                      ) : (
                                        <><ChevronDown className="w-3.5 h-3.5 -rotate-90" /> Expand</>
                                      )}
                                    </Button>
                                  </CollapsibleTrigger>
                                </div>
                                <CollapsibleContent>
                                  <div className="relative group">
                                    <button
                                      type="button"
                                      onClick={() => {
                                        const toCopy = normalizeCodeIndent(displayCode);
                                        navigator.clipboard.writeText(toCopy).then(
                                          () => toast.success('Code copied to clipboard'),
                                          () => toast.error('Failed to copy')
                                        );
                                      }}
                                      className="absolute top-2 right-2 z-10 p-1.5 rounded-md bg-background/80 border border-border/50 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                                      title="Copy code"
                                      aria-label="Copy code"
                                    >
                                      <Copy className="w-4 h-4" />
                                    </button>
                                    <pre className="text-xs font-mono bg-muted/30 border border-border/50 rounded-lg p-4 overflow-x-auto text-left text-foreground/90 pr-12" style={{ whiteSpace: 'pre', margin: 0 }}>
                                      {normalizeCodeIndent(displayCode)}
                                    </pre>
                                  </div>
                                </CollapsibleContent>
                              </Collapsible>
                            </div>
                          ) : null;
                        })()}
                        {approach.complexity != null && approach.complexity !== '' && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2">Time & Space Complexity</h4>
                            <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{approach.complexity}</p>
                          </div>
                        )}
                        {approach.content != null && approach.content !== '' && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2">Explanation</h4>
                            <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{approach.content}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Common Pitfalls - aligned with card styling */}
                  {problem.common_pitfalls && (
                    <div className="rounded-lg border border-border/50 bg-card/30 overflow-hidden">
                      <h3 className="px-4 py-3 border-b border-border/50 font-semibold text-base text-foreground">
                        Common Pitfalls
                      </h3>
                      <p className="px-4 py-4 text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                        {problem.common_pitfalls}
                      </p>
                    </div>
                  )}
                </div>
              ) : problem?.solution ? (
                <div className="rounded-lg border border-border/50 bg-card/30 overflow-hidden p-4">
                  <h3 className="font-semibold text-base text-foreground mb-3">Solution</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{problem.solution}</p>
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">Solution approach and walkthrough can be added here.</p>
              )}
              </div>
            </TabsContent>

            <TabsContent value="submissions" className="mt-6">
              <div className="flex flex-wrap gap-2 mb-4">
                <Select value={submissionFilterStatus || 'all'} onValueChange={(v) => setSubmissionFilterStatus(v === 'all' ? '' : v)}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All statuses</SelectItem>
                    <SelectItem value="accepted">Accepted</SelectItem>
                    <SelectItem value="wrong_answer">Wrong Answer</SelectItem>
                    <SelectItem value="time_limit_exceeded">Time Limit Exceeded</SelectItem>
                    <SelectItem value="runtime_error">Runtime Error</SelectItem>
                    <SelectItem value="compile_error">Compile Error</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={submissionFilterLanguage || 'all'} onValueChange={(v) => setSubmissionFilterLanguage(v === 'all' ? '' : v)}>
                  <SelectTrigger className="w-36">
                    <SelectValue placeholder="Language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All languages</SelectItem>
                    <SelectItem value="python">Python</SelectItem>
                    <SelectItem value="javascript">JavaScript</SelectItem>
                    <SelectItem value="java">Java</SelectItem>
                    <SelectItem value="cpp">C++</SelectItem>
                    <SelectItem value="c">C</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {submissionsLoading ? (
                <p className="text-muted-foreground">Loading submissions...</p>
              ) : submissions.length === 0 ? (
                <p className="text-muted-foreground">No submissions yet. Submit your code to see history here.</p>
              ) : (
                <div className="space-y-3">
                  {submissions.map((sub) => (
                    <div
                      key={sub.id}
                      className="rounded-lg border border-border/50 bg-card/30 overflow-hidden"
                    >
                      <div
                        className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/20 flex-wrap gap-2"
                        onClick={() => setExpandedSubmissionId(expandedSubmissionId === sub.id ? null : sub.id)}
                      >
                        <div className="flex items-center gap-4 flex-wrap">
                          <span className={`text-sm font-medium ${STATUS_COLORS[sub.status] || 'text-muted-foreground'}`}>
                            {sub.status?.replace(/_/g, ' ')}
                          </span>
                          <span className="text-xs text-muted-foreground capitalize">{sub.language}</span>
                          <span className="text-xs text-muted-foreground">
                            {sub.created_at ? new Date(sub.created_at).toLocaleString() : ''}
                          </span>
                          {sub.result?.runtime != null && (
                            <span className="text-xs text-muted-foreground">{(sub.result.runtime)} ms</span>
                          )}
                        </div>
                        {sub.result && (
                          <span className="text-sm text-muted-foreground">
                            {sub.result.passed}/{sub.result.total} passed
                          </span>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {expandedSubmissionId === sub.id ? 'Hide code' : 'View code'}
                        </span>
                      </div>
                      {expandedSubmissionId === sub.id && sub.code && (
                        <div className="border-t border-border/50 p-4 bg-background/50">
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            className="mb-2"
                            onClick={() => {
                              setCode(sub.code);
                              setLanguage(sub.language);
                              toast.success('Code loaded. You can edit and submit again.');
                            }}
                          >
                            Use this code
                          </Button>
                          <pre className="text-xs font-mono whitespace-pre-wrap break-words max-h-48 overflow-y-auto">
                            {sub.code}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
            </div>
          </Panel>
          <PanelResizeHandle withHandle className="w-2 bg-border/50 hover:bg-primary/20 transition-colors data-[resize-handle-active]:bg-primary/30 shrink-0" />
          {/* Center Panel - Editor + Test Case + Run/Submit */}
          <Panel defaultSize={aiPanelOpen ? 33.33 : 60} minSize={25} maxSize={aiPanelOpen ? 50 : 80} className="flex flex-col min-w-0 min-h-0">
            <PanelGroup direction="vertical" className="flex-1 min-h-0 flex flex-col">
              <Panel defaultSize={75} minSize={40} className="flex flex-col min-h-0">
          {/* Editor toolbar: Language, Solution tabs, If Else AI, Hint, cursor position */}
          <div className="flex items-center justify-between px-3 py-1.5 border-b border-border/50 bg-card/20 shrink-0 gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <Select
                value={availableEditorLanguages.includes(language) ? language : (availableEditorLanguages[0] || 'python')}
                onValueChange={handleLanguageChange}
                data-testid="language-selector"
              >
                <SelectTrigger className="w-28 h-8 text-xs border-0 bg-transparent shadow-none focus:ring-0">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {availableEditorLanguages.map((lang) => (
                    <SelectItem key={lang} value={lang}>
                      {lang === 'cpp' ? 'C++' : lang === 'c' ? 'C' : lang.charAt(0).toUpperCase() + lang.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="h-4 w-px bg-border/60" />
              {solutionTabs.map((tab, idx) => (
                <div
                  key={tab.id}
                  className={`inline-flex items-center gap-1 px-3 py-1.5 text-sm rounded-t ${idx === activeSolutionIndex ? 'bg-background border border-border/50 border-b-0 -mb-px' : 'text-muted-foreground hover:text-foreground'}`}
                >
                  <button
                    type="button"
                    onClick={() => switchSolutionTab(idx)}
                    className="focus:outline-none"
                  >
                    {tab.name}
                  </button>
                  {solutionTabs.length > 1 && (
                    <button
                      type="button"
                      onClick={(e) => removeSolutionTab(idx, e)}
                      className="p-0.5 rounded hover:bg-muted focus:outline-none"
                      title="Close tab"
                      aria-label="Close tab"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={addSolutionTab}
                className="p-1.5 text-muted-foreground hover:text-foreground rounded"
                title="New solution"
              >
                +
              </button>
              <div className="h-4 w-px bg-border/60 mx-1" />
              <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs font-medium" onClick={() => setAiPanelOpen(true)} title="Open Hints">
                <Lightbulb className="w-3.5 h-3.5" />
                Hint
              </Button>
              <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs font-medium" onClick={() => setAiPanelOpen(true)} title="Open If Else AI">
                <IfElseIcon className="w-3.5 h-3.5" />
                If Else AI
              </Button>
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              Ln {cursorPos.line}, Col {cursorPos.column}
            </span>
          </div>
          <p className="px-3 py-1 text-xs text-muted-foreground bg-muted/20 border-b border-border/30 shrink-0">
            Implement only the solution function. Do not read input — the system will call your function with test inputs.
          </p>

          {/* Editor */}
          <div className="flex-1 min-h-0 overflow-hidden" data-testid="code-editor">
            <Editor
              height="100%"
              language={language === 'python' ? 'python' : language === 'javascript' ? 'javascript' : language === 'java' ? 'java' : language === 'cpp' ? 'cpp' : 'c'}
              value={code}
              onChange={(value) => setCurrentCode(value || '')}
              onMount={(editor) => {
                editorRef.current = editor;
                editor.onDidChangeCursorPosition((e) => setCursorPos({ line: e.position.lineNumber, column: e.position.column }));
              }}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: language === 'python' ? 4 : 2,
              }}
            />
          </div>
              </Panel>
              <PanelResizeHandle withHandle className="h-2 bg-border/50 hover:bg-primary/20 transition-colors data-[resize-handle-active]:bg-primary/30 shrink-0" />
              <Panel defaultSize={25} minSize={20} className="flex flex-col min-h-0 overflow-hidden">
          {/* Bottom: Test Case | Output + Console (Run/Submit moved to fixed bar below) */}
          <div className="border-t border-border/50 bg-card/30 flex flex-col flex-1 min-h-0 overflow-hidden overflow-y-auto">
            <Tabs value={bottomTab} onValueChange={setBottomTab} className="w-full flex flex-col flex-1 min-h-0">
              <div className="flex items-center justify-between px-3 py-2 border-b border-border/30">
                <TabsList className="h-8 bg-transparent p-0 gap-0">
                  <TabsTrigger value="testcase" className="gap-1.5 data-[state=active]:bg-muted/50 rounded px-3">
                    <Beaker className="w-4 h-4" />
                    Test Case
                  </TabsTrigger>
                  <TabsTrigger value="output" className="gap-1.5 data-[state=active]:bg-muted/50 rounded px-3">
                    <ArrowRight className="w-4 h-4" />
                    Output
                  </TabsTrigger>
                </TabsList>
              </div>
              <TabsContent value="testcase" className="mt-0 p-3 space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  {(problem?.test_cases ?? [])
                    .filter((tc) => !tc.is_hidden)
                    .map((_, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setActiveTestCaseIndex(idx)}
                        className={`px-3 py-1 text-sm rounded ${idx === activeTestCaseIndex ? 'bg-primary text-primary-foreground' : 'bg-muted/50 text-muted-foreground hover:text-foreground'}`}
                      >
                        Case {idx + 1}
                      </button>
                    ))}
                </div>
                {problem?.test_cases?.filter((tc) => !tc.is_hidden)[activeTestCaseIndex] && (
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Input:</span>
                      <pre className="mt-1 p-2 bg-background/50 rounded font-mono text-xs overflow-x-auto">
                        {problem.test_cases.filter((tc) => !tc.is_hidden)[activeTestCaseIndex].input}
                      </pre>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Expected:</span>
                      <pre className="mt-1 p-2 bg-background/50 rounded font-mono text-xs overflow-x-auto">
                        {problem.test_cases.filter((tc) => !tc.is_hidden)[activeTestCaseIndex].expected_output}
                      </pre>
                    </div>
                  </div>
                )}
                {/* Add custom test case — input only; run shows your output; no expected output asked */}
                <div className="border-t border-border/30 pt-3 space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">Add custom test case</p>
                  <p className="text-xs text-muted-foreground">Enter input only. Run will show your output; pass/fail is determined automatically when possible.</p>
                  <Textarea
                    placeholder="e.g. 2 7 11 15&#10;9"
                    value={newTestInput}
                    onChange={(e) => setNewTestInput(e.target.value)}
                    className="min-h-[60px] font-mono text-xs bg-background/50 resize-none"
                    rows={2}
                  />
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="gap-1"
                    onClick={() => {
                      if (!newTestInput.trim()) return;
                      setCustomTestCases((prev) => [...prev, { id: Date.now(), input: newTestInput.trim() }]);
                      setNewTestInput('');
                    }}
                  >
                    <Plus className="w-4 h-4" />
                    Add test case
                  </Button>
                </div>
                {customTestCases.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Your test cases ({customTestCases.length})</p>
                    {customTestCases.map((tc) => (
                      <div key={tc.id} className="flex items-start gap-2 p-2 bg-background/50 rounded border border-border/30 text-xs">
                        <div className="flex-1 min-w-0">
                          <span className="text-muted-foreground">Input:</span> <span className="font-mono break-all whitespace-pre-wrap">{tc.input}</span>
                        </div>
                        <Button type="button" variant="ghost" size="icon" className="shrink-0 h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => setCustomTestCases((prev) => prev.filter((c) => c.id !== tc.id))}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
                <Collapsible open={consoleOpen} onOpenChange={setConsoleOpen}>
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground -ml-1">
                      {consoleOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      Console
                    </Button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <pre className="mt-2 p-2 bg-background/50 rounded text-xs text-muted-foreground font-mono min-h-[2rem]">
                      {result?.result?.test_results?.[activeTestCaseIndex]?.output ?? 'No output'}
                    </pre>
                  </CollapsibleContent>
                </Collapsible>
              </TabsContent>
              <TabsContent value="output" className="mt-0 p-3">
                {result ? (
                  <div className="space-y-3 text-sm">
                    <div className="flex flex-wrap items-center gap-3">
                      {result.status === 'accepted' ? (
                        <Check className="w-5 h-5 text-green-400" />
                      ) : (
                        <X className="w-5 h-5 text-red-400" />
                      )}
                      <span className={STATUS_COLORS[result.status] || 'text-muted-foreground'}>
                        {result.status.replace(/_/g, ' ')}
                      </span>
                      <span className="text-muted-foreground">
                        {result.result?.passed}/{result.result?.total} passed
                      </span>
                      {result.result?.runtime != null && (
                        <span className="text-muted-foreground">Runtime: {result.result.runtime} ms</span>
                      )}
                      {result.result?.memory != null && (
                        <span className="text-muted-foreground">Memory: {result.result.memory}</span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground font-medium">Test case breakdown</p>
                    {result.result?.test_results?.map((tr, idx) => (
                      <div
                        key={idx}
                        className={`p-2 rounded text-xs border ${
                          tr.passed ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'
                        }`}
                      >
                        Case {tr.test_case}: {tr.passed ? 'Passed' : 'Failed'}
                        {tr.custom && <span className="text-muted-foreground ml-1">(Custom)</span>}
                        {tr.runtime != null && <span className="ml-2 text-muted-foreground">({tr.runtime} ms)</span>}
                        {tr.output != null && <div className="mt-1 font-mono break-all">Output: {tr.output}</div>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">Run or submit to see output.</p>
                )}
              </TabsContent>
            </Tabs>
          </div>
              </Panel>
            </PanelGroup>
            {/* Fixed Run/Submit bar — always visible at bottom of editor column */}
            <div className="shrink-0 flex justify-end gap-2 px-3 py-2 border-t border-border/50 bg-background/80">
              <Button variant="outline" size="sm" onClick={handleRun} disabled={running || submitting} data-testid="run-code-btn">
                {running ? 'Running...' : 'Run'}
              </Button>
              <Button size="sm" onClick={handleSubmit} disabled={submitting || running} data-testid="submit-code-btn" className="bg-primary">
                {submitting ? 'Submitting...' : 'Submit'}
              </Button>
            </div>
          </Panel>
          {aiPanelOpen && (
            <>
              <PanelResizeHandle withHandle className="w-2 bg-border/50 hover:bg-primary/20 transition-colors data-[resize-handle-active]:bg-primary/30 shrink-0" />
              <Panel defaultSize={33.34} minSize={20} maxSize={50} className="flex flex-col min-h-0 bg-card/20 border-l border-border/50">
                <AICoachPanel
                  problemId={problemId}
                  problem={problem}
                  code={code}
                  language={language}
                  submissionStatus={result?.status}
                  failingTestInfo={result?.result?.test_results?.[0] ? `Expected: ${result.result.test_results[0].expected}\nGot: ${result.result.test_results[0].output}` : undefined}
                  onClose={() => setAiPanelOpen(false)}
                />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
};

export default ProblemSolvePage;
