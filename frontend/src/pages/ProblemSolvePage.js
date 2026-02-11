import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Code2, Play, Check, X, Clock, ArrowLeft } from 'lucide-react';
import { DIFFICULTY_COLORS, STATUS_COLORS } from '@/utils/constants';
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

const ProblemSolvePage = () => {
  const { problemId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProblem();
  }, [problemId, user]);

  const fetchProblem = async () => {
    try {
      const response = await api.get(`/problems/${problemId}`);
      setProblem(response.data);
      
      // Set starter code
      if (language === 'python') {
        setCode(response.data.starter_code_python || '# Write your code here');
      } else {
        setCode(response.data.starter_code_javascript || '// Write your code here');
      }
    } catch (error) {
      toast.error('Failed to load problem');
      navigate('/problems');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    if (problem) {
      if (newLanguage === 'python') {
        setCode(problem.starter_code_python || '# Write your code here');
      } else {
        setCode(problem.starter_code_javascript || '// Write your code here');
      }
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
      
      if (response.data.status === 'accepted') {
        toast.success('All test cases passed!');
      } else {
        toast.error('Some test cases failed');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading problem...</p>
      </div>
    );
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b border-border/50 bg-card/30 px-6 py-3 flex items-center justify-between">
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
        </div>
        <div className="flex items-center gap-4">
          <Select value={language} onValueChange={handleLanguageChange} data-testid="language-selector">
            <SelectTrigger className="w-40 bg-card border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)]"
            data-testid="submit-code-btn"
          >
            <Play className="w-4 h-4 mr-2" />
            {submitting ? 'Running...' : 'Run Code'}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Problem Description */}
        <div className="w-1/2 border-r border-border/50 overflow-y-auto p-6" data-testid="problem-description">
          <Tabs defaultValue="description" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-muted/30">
              <TabsTrigger value="description">Description</TabsTrigger>
              <TabsTrigger value="submissions">Submissions</TabsTrigger>
            </TabsList>
            
            <TabsContent value="description" className="space-y-6 mt-6">
              <div>
                <h2 className="font-heading font-semibold text-xl mb-2">Description</h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-muted-foreground whitespace-pre-wrap">{problem?.description}</p>
                </div>
              </div>

              {problem?.tags && problem.tags.length > 0 && (
                <div>
                  <h3 className="font-heading font-medium text-lg mb-2">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {problem.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-sm px-3 py-1 bg-accent/10 text-accent rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {problem?.companies && problem.companies.length > 0 && (
                <div>
                  <h3 className="font-heading font-medium text-lg mb-2">Companies</h3>
                  <div className="flex flex-wrap gap-2">
                    {problem.companies.map((company) => (
                      <span
                        key={company}
                        className="text-sm px-3 py-1 bg-secondary/10 text-secondary rounded-full"
                      >
                        {company}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="font-heading font-medium text-lg mb-2">Test Cases</h3>
                <div className="space-y-4">
                  {problem?.test_cases
                    ?.filter((tc) => !tc.is_hidden)
                    .map((testCase, idx) => (
                      <div key={idx} className="bg-muted/20 rounded-lg p-4 border border-border/30">
                        <div className="mb-2">
                          <span className="text-sm font-medium text-muted-foreground">Input:</span>
                          <pre className="mt-1 text-sm font-code bg-background/50 p-2 rounded">
                            {testCase.input}
                          </pre>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-muted-foreground">Expected Output:</span>
                          <pre className="mt-1 text-sm font-code bg-background/50 p-2 rounded">
                            {testCase.expected_output}
                          </pre>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="submissions" className="mt-6">
              <p className="text-muted-foreground">Your submission history will appear here</p>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Panel - Code Editor */}
        <div className="w-1/2 flex flex-col">
          {/* Editor */}
          <div className="flex-1 overflow-hidden" data-testid="code-editor">
            <Editor
              height="100%"
              language={language === 'python' ? 'python' : 'javascript'}
              value={code}
              onChange={(value) => setCode(value || '')}
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

          {/* Results Panel */}
          {result && (
            <div className="border-t border-border/50 bg-card/30 p-4 max-h-64 overflow-y-auto" data-testid="results-panel">
              <div className="flex items-center gap-2 mb-4">
                {result.status === 'accepted' ? (
                  <>
                    <Check className="w-5 h-5 text-green-400" />
                    <span className="font-heading font-semibold text-lg text-green-400">
                      Accepted
                    </span>
                  </>
                ) : (
                  <>
                    <X className="w-5 h-5 text-red-400" />
                    <span className="font-heading font-semibold text-lg text-red-400">
                      {result.status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </span>
                  </>
                )}
                <span className="text-sm text-muted-foreground ml-auto">
                  {result.result?.passed} / {result.result?.total} test cases passed
                </span>
              </div>

              <div className="space-y-2">
                {result.result?.test_results.map((testResult, idx) => (
                  <div
                    key={idx}
                    className={`border rounded-lg p-3 ${
                      testResult.passed
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-red-500/30 bg-red-500/5'
                    }`}
                    data-testid={`test-result-${idx}`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {testResult.passed ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <X className="w-4 h-4 text-red-400" />
                      )}
                      <span className="font-medium text-sm">Test Case {testResult.test_case}</span>
                      {testResult.runtime && (
                        <span className="text-xs text-muted-foreground ml-auto flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {testResult.runtime}ms
                        </span>
                      )}
                    </div>
                    {!testResult.hidden && (
                      <div className="text-xs space-y-1 font-code">
                        <div>
                          <span className="text-muted-foreground">Input: </span>
                          <span>{testResult.input}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Expected: </span>
                          <span>{testResult.expected}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Output: </span>
                          <span className={testResult.passed ? 'text-green-400' : 'text-red-400'}>
                            {testResult.output}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProblemSolvePage;
