import React, { useState, useEffect } from 'react';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import IfElseIcon from '@/components/IfElseIcon';
import { Lightbulb, MessageSquare, Bug, BookOpen, Code, ChevronDown, ChevronRight, ChevronUp, Loader2, PanelLeft, PanelBottom, PanelRight, X } from 'lucide-react';
import { toast } from 'sonner';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const MODES = [
  { id: 'hint', label: 'Hint', icon: Lightbulb },
  { id: 'code_review', label: 'Code review', icon: Code },
  { id: 'debug', label: 'Debug help', icon: Bug },
  { id: 'concept', label: 'Explain concept', icon: BookOpen },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
];

export default function AICoachPanel({ problemId, problem, code, language, submissionStatus, failingTestInfo, onClose, panelPosition = 'right', onMoveTo }) {
  const [mode, setMode] = useState('hint');
  const [hintLevel, setHintLevel] = useState(1);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [showSolutionConfirm, setShowSolutionConfirm] = useState(false);
  const [fullSolutionText, setFullSolutionText] = useState('');

  // Hint-mode state (progressive hints)
  const [aiHintContent, setAiHintContent] = useState({});
  const [solutionOpen, setSolutionOpen] = useState(false);
  const [codeSnippetsOpen, setCodeSnippetsOpen] = useState(false);
  const [optionalInstructions, setOptionalInstructions] = useState('');
  const [solutionLoading, setSolutionLoading] = useState(false);
  const [loadingLevel, setLoadingLevel] = useState(null);

  const hints = problem?.hints ?? [];
  // Code-based hint: AI-generated hint that uses the user's current code (separate from problem hints)
  const [codeBasedHintText, setCodeBasedHintText] = useState('');
  const [codeBasedHintLoading, setCodeBasedHintLoading] = useState(false);
  const [codeBasedHintOpen, setCodeBasedHintOpen] = useState(false);
  const [problemHintsOpen, setProblemHintsOpen] = useState({ 0: true });

  const send = async (payload, endpoint) => {
    if (!problemId) return;
    setLoading(true);
    setResponse('');
    try {
      const { data } = await api.post(`/coach/${endpoint}`, payload);
      const text = data.text ?? data.feedback ?? '';
      setResponse(text);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Request failed';
      toast.error(typeof msg === 'string' ? msg : 'If Else AI request failed');
      setResponse('');
    } finally {
      setLoading(false);
    }
  };

  const requestHint = async (level) => {
    if (!problemId) return;
    setLoading(true);
    setLoadingLevel(level);
    try {
      const { data } = await api.post('/coach/hint', {
        problem_id: problemId,
        code: code || '',
        hint_level: level,
        ...(optionalInstructions.trim() ? { extra_instructions: optionalInstructions.trim() } : {}),
      });
      const text = data.text ?? data.feedback ?? '';
      setAiHintContent((prev) => ({ ...prev, [level]: text }));
    } catch (err) {
      const msg = err.response?.data?.detail || 'Request failed';
      toast.error(typeof msg === 'string' ? msg : 'If Else AI request failed');
    } finally {
      setLoading(false);
      setLoadingLevel(null);
    }
  };

  const requestCodeBasedHint = async () => {
    if (!problemId) return;
    setCodeBasedHintLoading(true);
    setCodeBasedHintOpen(true);
    try {
      const { data } = await api.post('/coach/hint', {
        problem_id: problemId,
        code: code || '',
        hint_level: 1,
        ...(optionalInstructions.trim() ? { extra_instructions: optionalInstructions.trim() } : {}),
      });
      const text = data.text ?? data.feedback ?? '';
      setCodeBasedHintText(text);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Request failed';
      toast.error(typeof msg === 'string' ? msg : 'If Else AI request failed');
    } finally {
      setCodeBasedHintLoading(false);
    }
  };

  const handleHint = () => {
    send(
      { problem_id: problemId, code: code || '', hint_level: hintLevel },
      'hint'
    );
  };

  const handleCodeReview = () => {
    send(
      {
        problem_id: problemId,
        code: code || '',
        language: language || 'python',
        status: submissionStatus || 'pending',
      },
      'code-review'
    );
  };

  const handleDebug = () => {
    send(
      {
        problem_id: problemId,
        code: code || '',
        status: submissionStatus || 'wrong_answer',
        failing_test_info: failingTestInfo,
      },
      'debug'
    );
  };

  const handleConcept = () => {
    send({ problem_id: problemId }, 'explain-concept');
  };

  const handleChat = () => {
    const msg = (chatInput || '').trim();
    if (!msg) {
      toast.error('Enter a message');
      return;
    }
    send({ problem_id: problemId, message: msg }, 'chat');
    setChatInput('');
  };

  const handleRetry = () => {
    if (mode === 'hint') {
      requestCodeBasedHint();
    } else {
      if (mode === 'code_review') handleCodeReview();
      else if (mode === 'debug') handleDebug();
      else if (mode === 'concept') handleConcept();
    }
  };

  const handleFullSolution = () => {
    if (!showSolutionConfirm) {
      setShowSolutionConfirm(true);
      return;
    }
    setSolutionLoading(true);
    api
      .post('/coach/full-solution', {
        problem_id: problemId,
        request_text: 'Give me the full solution',
      })
      .then(({ data }) => {
        setFullSolutionText(data.text ?? data.feedback ?? '');
        setShowSolutionConfirm(false);
      })
      .catch(() => {
        toast.error('If Else AI request failed');
      })
      .finally(() => setSolutionLoading(false));
  };

  const solutionCode = problem?.solutions?.[0];
  const codeSnippetText =
    solutionCode &&
    (solutionCode.code_python ||
      solutionCode.code ||
      solutionCode.code_javascript ||
      solutionCode.code_java ||
      solutionCode.code_cpp ||
      solutionCode.code_c);

  useEffect(() => {
    setAiHintContent({});
    setCodeBasedHintText('');
    setCodeBasedHintOpen(false);
    setProblemHintsOpen({ 0: true });
    setFullSolutionText('');
    setResponse('');
    setSolutionOpen(false);
    setCodeSnippetsOpen(false);
    setShowSolutionConfirm(false);
  }, [problemId]);

  /** Parse inline **bold** and return React nodes */
  const parseBold = (s) => {
    if (typeof s !== 'string') return s;
    const parts = s.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) =>
      part.startsWith('**') && part.endsWith('**')
        ? React.createElement('strong', { key: i, className: 'font-semibold text-foreground' }, part.slice(2, -2))
        : part
    );
  };

  /** Format code review response: sections, bold headers, bullet lists */
  const formatCodeReviewResponse = (text) => {
    if (!text || typeof text !== 'string') return null;
    const lines = text.split('\n');
    const elements = [];
    let listItems = [];
    const flushList = () => {
      if (listItems.length > 0) {
        elements.push(
          React.createElement('ul', { key: elements.length, className: 'list-disc pl-4 mt-1 space-y-0.5 text-muted-foreground' }, ...listItems)
        );
        listItems = [];
      }
    };
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      if (trimmed.startsWith('- ')) {
        listItems.push(
          React.createElement('li', { key: listItems.length }, parseBold(trimmed.slice(2)))
        );
      } else if (trimmed === '') {
        flushList();
      } else {
        flushList();
        const isSectionHeader = trimmed.startsWith('**') && trimmed.includes('**');
        elements.push(
          React.createElement(
            'p',
            {
              key: elements.length,
              className: isSectionHeader ? 'font-semibold text-foreground mt-3 first:mt-0' : 'text-muted-foreground mt-1',
            },
            parseBold(trimmed)
          )
        );
      }
    }
    flushList();
    return elements;
  };

  const renderResponse = (text, useCodeReviewFormat = false) => {
    if (!text) return null;
    const content =
      useCodeReviewFormat && mode === 'code_review'
        ? formatCodeReviewResponse(text)
        : text;
    return (
      <div className="mt-3 p-3 rounded-lg bg-muted/30 border border-border/50 text-sm text-foreground/90">
        {useCodeReviewFormat && mode === 'code_review' ? (
          <div className="space-y-0 first:mt-0">{content}</div>
        ) : (
          <span className="whitespace-pre-wrap">{content}</span>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Header: If Else AI + Move to + close */}
      <div className="shrink-0 px-3 py-2.5 border-b border-border/50 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
            <IfElseIcon className="w-3.5 h-3.5 text-white" />
          </span>
          If Else AI
        </span>
        <span className="flex items-center gap-1">
          {typeof onMoveTo === 'function' && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-7 text-xs text-muted-foreground hover:text-foreground gap-1.5">
                  Move to:
                  <ChevronDown className="w-3.5 h-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="min-w-[10rem]">
                <DropdownMenuItem onClick={() => onMoveTo('left')} className={panelPosition === 'left' ? 'bg-primary/10 text-primary' : ''}>
                  <PanelLeft className="w-4 h-4 mr-2" />
                  Left Panel
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onMoveTo('console')} className={panelPosition === 'console' ? 'bg-primary/10 text-primary' : ''}>
                  <PanelBottom className="w-4 h-4 mr-2" />
                  Console
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onMoveTo('right')} className={panelPosition === 'right' ? 'bg-primary/10 text-primary' : ''}>
                  <PanelRight className="w-4 h-4 mr-2" />
                  Right Panel
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          {typeof onClose === 'function' && (
            <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground" onClick={onClose} title="Close panel" aria-label="Close">
              <X className="w-4 h-4" />
            </Button>
          )}
        </span>
      </div>

      {/* Mode tabs: Hint | Code review | Debug | Explain concept | Chat */}
      <div className="shrink-0 px-2 py-2 border-b border-border/50 flex items-center gap-1 flex-wrap">
        {MODES.map((m) => (
          <Button
            key={m.id}
            variant={mode === m.id ? 'default' : 'ghost'}
            size="sm"
            className="h-8 text-xs"
            onClick={() => { setMode(m.id); setResponse(''); setShowSolutionConfirm(false); }}
          >
            <m.icon className="w-3.5 h-3.5 mr-1" />
            {m.label}
          </Button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto flex flex-col min-h-0 p-3">
        {/* Hint tab: progressive hints + optional instructions + Retry */}
        {mode === 'hint' && (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Lightbulb className="w-4 h-4 text-primary" />
                Hints
              </span>
            </div>
            {/* Problem hints (same as left panel) */}
            <div className="space-y-0">
              {hints.map((hint, i) => (
                <Collapsible
                  key={i}
                  open={!!problemHintsOpen[i]}
                  onOpenChange={(open) => setProblemHintsOpen((prev) => ({ ...prev, [i]: open }))}
                >
                  <CollapsibleTrigger asChild>
                    <button
                      type="button"
                      className="w-full flex items-center justify-between py-2.5 px-3 rounded-md hover:bg-muted/30 text-left text-sm font-medium"
                    >
                      <span className="flex items-center gap-2">
                        {problemHintsOpen[i] ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronRight className="w-4 h-4 text-muted-foreground" />}
                        Hint {i + 1}
                      </span>
                    </button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="px-3 pb-3 text-sm text-muted-foreground whitespace-pre-wrap border-b border-border/30">
                      {hint}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              ))}
            </div>
            {/* Hints based on your code (AI-generated using current code) */}
            <Collapsible open={codeBasedHintOpen} onOpenChange={setCodeBasedHintOpen} className="mt-1">
              <CollapsibleTrigger asChild>
                <button
                  type="button"
                  className="w-full flex items-center justify-between py-2.5 px-3 rounded-md hover:bg-muted/30 text-left text-sm font-medium"
                >
                  <span className="flex items-center gap-2">
                    {codeBasedHintOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    Hints based on your code
                  </span>
                  {!codeBasedHintOpen && !codeBasedHintText && <span className="text-xs text-muted-foreground">Click to reveal</span>}
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="px-3 pb-3 border-b border-border/30 space-y-2">
                  {codeBasedHintLoading ? (
                    <span className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="w-4 h-4 animate-spin" /> Loading…
                    </span>
                  ) : codeBasedHintText ? (
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">{codeBasedHintText}</p>
                  ) : (
                    <Button size="sm" variant="outline" className="gap-2" onClick={requestCodeBasedHint}>
                      <Lightbulb className="w-3.5 h-3.5" />
                      Get hints based on your code
                    </Button>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
            <Collapsible open={solutionOpen} onOpenChange={setSolutionOpen} className="mt-1">
              <CollapsibleTrigger asChild>
                <button
                  type="button"
                  className="w-full flex items-center justify-between py-2.5 px-3 rounded-md hover:bg-muted/30 text-left text-sm font-medium"
                >
                  <span className="flex items-center gap-2">
                    {solutionOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    Solution (reveals answer)
                  </span>
                  {!solutionOpen && <span className="text-xs text-muted-foreground">Click to reveal</span>}
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="px-3 pb-3 border-b border-border/30 space-y-2">
                  {!fullSolutionText ? (
                    <>
                      <p className="text-xs text-muted-foreground">Only use when you need the complete solution. Try hints first.</p>
                      {showSolutionConfirm ? (
                        <div className="flex gap-2">
                          <Button size="sm" variant="default" onClick={handleFullSolution} disabled={solutionLoading}>
                            {solutionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                            Yes, show solution
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setShowSolutionConfirm(false)}>Cancel</Button>
                        </div>
                      ) : (
                        <Button size="sm" variant="outline" onClick={() => setShowSolutionConfirm(true)}>I want the full solution</Button>
                      )}
                    </>
                  ) : (
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">{fullSolutionText}</p>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
            <Collapsible open={codeSnippetsOpen} onOpenChange={setCodeSnippetsOpen} className="mt-1">
              <CollapsibleTrigger asChild>
                <button
                  type="button"
                  className="w-full flex items-center justify-between py-2.5 px-3 rounded-md hover:bg-muted/30 text-left text-sm font-medium"
                >
                  <span className="flex items-center gap-2">
                    {codeSnippetsOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    Code Snippets
                  </span>
                  {!codeSnippetsOpen && <span className="text-xs text-muted-foreground">Click to reveal</span>}
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="px-3 pb-3">
                  {codeSnippetText ? (
                    <pre className="text-xs font-mono bg-muted/30 rounded p-3 overflow-x-auto whitespace-pre text-left">{codeSnippetText}</pre>
                  ) : (
                    <p className="text-xs text-muted-foreground">No code snippets for this problem.</p>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
            <div className="mt-3 space-y-2">
              <Textarea
                placeholder="Add instructions for different hints (optional)..."
                value={optionalInstructions}
                onChange={(e) => setOptionalInstructions(e.target.value)}
                className="min-h-[52px] text-xs resize-none bg-muted/20 border-border/50"
                maxLength={500}
              />
              <Button size="sm" variant="default" className="w-full gap-2" onClick={handleRetry} disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                Retry
              </Button>
            </div>
          </>
        )}

        {/* Code review tab */}
        {mode === 'code_review' && (
          <>
            <Button size="sm" onClick={handleCodeReview} disabled={loading} className="gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Code className="w-4 h-4" />}
              Review my code
            </Button>
            {renderResponse(response, true)}
          </>
        )}

        {/* Debug tab */}
        {mode === 'debug' && (
          <>
            <Button size="sm" onClick={handleDebug} disabled={loading} className="gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Bug className="w-4 h-4" />}
              Help me debug
            </Button>
            {renderResponse(response)}
          </>
        )}

        {/* Explain concept tab */}
        {mode === 'concept' && (
          <>
            <Button size="sm" onClick={handleConcept} disabled={loading} className="gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <BookOpen className="w-4 h-4" />}
              Explain concept
            </Button>
            {renderResponse(response)}
          </>
        )}

        {/* Chat tab */}
        {mode === 'chat' && (
          <>
            <Textarea
              placeholder="Ask about approach, edge cases, or complexity..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="min-h-[80px] text-sm resize-none"
              maxLength={2000}
            />
            <Button size="sm" onClick={handleChat} disabled={loading || !chatInput.trim()} className="mt-2 gap-2 shrink-0 w-fit">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquare className="w-4 h-4" />}
              Send
            </Button>
            {renderResponse(response)}
          </>
        )}

        {/* Show full solution - available in all modes */}
        <div className="mt-auto pt-3 border-t border-border/30">
          <Collapsible>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="text-xs text-muted-foreground hover:text-foreground w-full justify-start gap-1">
                Show full solution {showSolutionConfirm ? <ChevronUp className="w-3 h-3 ml-1" /> : <ChevronDown className="w-3 h-3 ml-1" />}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <p className="text-xs text-muted-foreground mt-1 mb-2">Only use when you need the complete solution. Try hints first.</p>
              {showSolutionConfirm ? (
                <div className="flex gap-2">
                  <Button size="sm" variant="destructive" onClick={handleFullSolution} disabled={solutionLoading}>
                    {solutionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Yes, show solution'}
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setShowSolutionConfirm(false)}>Cancel</Button>
                </div>
              ) : (
                <Button size="sm" variant="outline" onClick={() => setShowSolutionConfirm(true)}>I want the full solution</Button>
              )}
            </CollapsibleContent>
          </Collapsible>
        </div>
      </div>
    </div>
  );
}
