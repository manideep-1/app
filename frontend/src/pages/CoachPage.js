import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api, { API_BASE } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { ArrowLeft, MessageSquarePlus, Trash2, Send, Loader2 } from 'lucide-react';
import CoachMessageContent from '@/components/CoachMessageContent';
import { toast } from 'sonner';

const COACH_API_BASE_LABEL = API_BASE === '/api' ? 'http://127.0.0.1:8000/api' : API_BASE;

export default function CoachPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [problemContext, setProblemContext] = useState(null);
  const messagesEndRef = useRef(null);
  const sessionsLoadingRef = useRef(false);
  const skipClearMessagesRef = useRef(false);
  const currentSessionIdRef = useRef(currentSessionId);
  currentSessionIdRef.current = currentSessionId;

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate('/login', { state: { from: '/coach' } });
      return;
    }
    loadSessions();
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (location.state?.problemContext) {
      setProblemContext(location.state.problemContext);
      if (location.state.problemId) {
        setProblemContext((prev) => ({ ...prev, problemId: location.state.problemId }));
      }
    }
  }, [location.state]);

  useEffect(() => {
    if (!currentSessionId) {
      setMessages([]);
      return;
    }
    if (!skipClearMessagesRef.current) setMessages([]);
    skipClearMessagesRef.current = false;
    loadSessionMessages(currentSessionId);
  }, [currentSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    if (sessionsLoadingRef.current) return;
    sessionsLoadingRef.current = true;
    try {
      const { data } = await api.get('coach/session-list');
      setSessions(data.sessions || []);
      if (!currentSessionId && (data.sessions || []).length > 0) {
        setCurrentSessionId(data.sessions[0].id);
      }
    } catch (err) {
      const status = err.response?.status;
      const noResponse = !err.response;
      const detail = err.response?.data?.detail ?? err.message ?? 'Failed to load sessions';
      let hint = 'Failed to load sessions';
      if (noResponse) {
        hint = `Cannot reach backend at ${COACH_API_BASE_LABEL}. Start it with: cd backend && uvicorn server:app --reload`;
      } else if (status === 404) {
        hint = `Coach API not found at ${COACH_API_BASE_LABEL}/coach/session-list. Start backend: cd backend && uvicorn server:app --reload`;
      } else if (typeof detail === 'string') {
        hint = detail;
      }
      toast.error(hint);
    } finally {
      sessionsLoadingRef.current = false;
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      const { data } = await api.get(`coach/sessions/${sessionId}`);
      const list = data.messages || [];
      setMessages((prev) => {
        if (currentSessionIdRef.current !== sessionId) return prev;
        return list;
      });
    } catch (_) {
      setMessages((prev) => (currentSessionIdRef.current === sessionId ? [] : prev));
    }
  };

  const createSession = async () => {
    try {
      const { data } = await api.post('coach/sessions');
      setSessions((prev) => [{ id: data.id, title: data.title || 'New chat', created_at: data.created_at }, ...prev]);
      setCurrentSessionId(data.id);
      setMessages([]);
      setProblemContext(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create session');
    }
  };

  const deleteSession = async (e, sessionId) => {
    e.stopPropagation();
    try {
      await api.delete(`coach/sessions/${sessionId}`);
      const nextList = sessions.filter((s) => s.id !== sessionId);
      setSessions(nextList);
      if (currentSessionId === sessionId) {
        setCurrentSessionId(nextList[0]?.id || null);
        setMessages([]);
      }
      toast.success('Session deleted');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete');
    }
  };

  const sendMessage = async () => {
    const msg = (input || '').trim();
    if (!msg || sending) return;
    setInput('');
    setSending(true);
    const userMsg = { role: 'user', content: msg, id: `u-${Date.now()}` };
    setMessages((prev) => [...prev, userMsg]);
    let sessionId = currentSessionId;
    try {
      const payload = {
        message: msg,
      };
      if (sessionId) payload.session_id = sessionId;
      if (problemContext?.problemId) payload.problem_id = problemContext.problemId;
      if (problemContext) {
        payload.problem_context = {
          title: problemContext.title ?? '',
          description: problemContext.description ?? '',
          examples_text: problemContext.examples_text ?? '',
          examples: problemContext.examples ?? '',
          difficulty: problemContext.difficulty ?? 'medium',
          tags: Array.isArray(problemContext.tags) ? problemContext.tags : [],
        };
        if (problemContext.userCode != null) payload.user_code = String(problemContext.userCode);
        if (problemContext.language != null) payload.language = String(problemContext.language);
      }
      const { data } = await api.post('coach/chat/session', payload);
      const reply = data?.reply ?? (typeof data?.text === 'string' ? data.text : '');
      const action = data?.action ?? null;
      sessionId = data?.session_id ?? sessionId;
      if (!currentSessionId && sessionId) {
        skipClearMessagesRef.current = true;
        setCurrentSessionId(sessionId);
        setSessions((prev) => [{ id: sessionId, title: msg.length > 50 ? msg.slice(0, 50) + '…' : msg, created_at: new Date().toISOString() }, ...prev]);
      }
      setMessages((prev) => [...prev, { role: 'assistant', content: reply || 'No response.', id: `a-${Date.now()}` }]);
      if (action?.type === 'prep_plan_created') {
        toast.success('Preparation plan created. Redirecting to My Plan...');
        navigate(action?.redirect_to || '/my-plan');
      } else if (action?.type === 'prep_plan_exists') {
        toast.message('You already have an active preparation plan. Open My Plan to continue.');
      }
    } catch (err) {
      const status = err.response?.status;
      const noResponse = !err.response;
      const detail = err.response?.data?.detail ?? err.message ?? 'Something went wrong';
      const msgList = Array.isArray(detail) ? detail.map((o) => o?.msg ?? o).join(', ') : String(detail);
      const msg = noResponse
        ? `Cannot reach backend at ${COACH_API_BASE_LABEL}. Start backend: cd backend && uvicorn server:app --reload`
        : status === 404
          ? `Coach API not found. Start backend: cd backend && uvicorn server:app --reload. URL: ${COACH_API_BASE_LABEL}/coach/chat/session`
          : msgList;
      toast.error(msg);
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    } finally {
      setSending(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      <header className="border-b border-border/50 bg-card/30 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Home
            </Button>
          </Link>
          <Link to="/my-plan">
            <Button variant="ghost" size="sm">My Plan</Button>
          </Link>
          <span className="font-heading font-semibold text-xl">If Else Coach</span>
          {problemContext?.title && (
            <span className="text-sm text-muted-foreground truncate max-w-[200px]" title={problemContext.title}>
              · {problemContext.title}
            </span>
          )}
        </div>
        <div className="rounded-full border border-border/60 px-3 py-1 text-xs text-muted-foreground">
          Preparation mode
        </div>
      </header>

      <div className="flex-1 flex min-h-0">
        <aside className="w-64 border-r border-border/50 bg-card/20 flex flex-col shrink-0">
          <div className="p-2 border-b border-border/50">
            <Button onClick={createSession} variant="outline" size="sm" className="w-full justify-start gap-2" data-testid="coach-new-chat">
              <MessageSquarePlus className="w-4 h-4" />
              New Chat
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.map((s) => (
              <div
                key={s.id}
                role="button"
                tabIndex={0}
                onClick={() => setCurrentSessionId(s.id)}
                onKeyDown={(e) => e.key === 'Enter' && setCurrentSessionId(s.id)}
                className={`group flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm truncate cursor-pointer ${currentSessionId === s.id ? 'bg-primary/15 text-foreground' : 'hover:bg-muted/50 text-muted-foreground hover:text-foreground'}`}
              >
                <span className="flex-1 min-w-0 truncate">{s.title || 'New chat'}</span>
                <button
                  type="button"
                  onClick={(e) => deleteSession(e, s.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-all"
                  aria-label="Delete session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && !sending && (
              <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground max-w-md mx-auto">
                <MessageSquarePlus className="w-12 h-12 mb-4 opacity-50" />
                <p className="font-medium text-foreground">Start a conversation</p>
                <p className="text-sm mt-1">
                  {problemContext?.title
                    ? `You're in problem context: ${problemContext.title}. Ask for prep strategy, debugging help, or interview-focused guidance.`
                    : 'Ask about DSA prep, interview strategy, or get a personalized roadmap.'}
                </p>
              </div>
            )}
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-3 ${
                    m.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted/60 text-foreground border border-border/50'
                  }`}
                >
                  <CoachMessageContent content={m.content} />
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="rounded-xl px-4 py-3 bg-muted/60 border border-border/50 flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-border/50 p-4 bg-card/20">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={problemContext?.title ? 'Ask about this problem...' : 'Ask anything about DSA or interview prep...'}
                className="flex-1 min-w-0 rounded-lg border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                disabled={sending}
                data-testid="coach-input"
              />
              <Button type="submit" disabled={sending || !input.trim()} size="icon" className="shrink-0" data-testid="coach-send">
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </form>
            <p className="text-xs text-muted-foreground mt-2">
              Preparation mode: strategy-first guidance for interviews and DSA practice.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
