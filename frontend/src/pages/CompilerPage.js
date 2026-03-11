import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Play, ArrowLeft } from 'lucide-react';
import Editor from '@monaco-editor/react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

const DEFAULT_CODE = {
  python: `# Read from stdin and print
import sys
data = sys.stdin.read().strip()
print("Input:", data)
# Your code here
`,
  javascript: `// Variable 'input' contains the full stdin as string
console.log("Input:", input);
// Your code here
`,
  java: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        while (sc.hasNextLine()) {
            System.out.println(sc.nextLine());
        }
        sc.close();
    }
}
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    string line;
    while (getline(cin, line)) {
        cout << line << endl;
    }
    return 0;
}
`,
  c: `#include <stdio.h>

int main() {
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        printf("%s", line);
    }
    return 0;
}
`,
};

const LANG_EDITOR = {
  python: 'python',
  javascript: 'javascript',
  java: 'java',
  cpp: 'cpp',
  c: 'c',
};

const CompilerPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(DEFAULT_CODE.python);
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState(null);
  const [runtimeMs, setRuntimeMs] = useState(null);
  const [running, setRunning] = useState(false);


  React.useEffect(() => {
    setCode((prev) => {
      const next = DEFAULT_CODE[language];
      return next !== undefined ? next : prev;
    });
  }, [language]);

  const handleRun = async () => {
    if (!user) {
      toast.error('Please log in to run code');
      navigate('/login');
      return;
    }
    setRunning(true);
    setOutput('');
    setError(null);
    setRuntimeMs(null);
    try {
      const res = await api.post('/run/playground', {
        code,
        language,
        input: input || '',
      });
      setOutput(res.data.output ?? '');
      setError(res.data.error ?? null);
      setRuntimeMs(res.data.runtime_ms ?? null);
      if (res.data.error) {
        toast.error('Run failed');
      } else {
        toast.success('Run completed');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Run failed';
      setError(String(msg));
      toast.error(msg);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      <header className="border-b border-border/50 bg-card/30 px-6 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/" data-testid="compiler-back-home">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Home
            </Button>
          </Link>
          <span className="font-heading font-semibold text-xl">Compiler</span>
        </div>
        <div className="flex items-center gap-2">
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-36">
              <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
              <SelectItem value="java">Java</SelectItem>
              <SelectItem value="cpp">C++</SelectItem>
              <SelectItem value="c">C</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleRun}
            disabled={running}
            className="bg-green-600 hover:bg-green-700"
            data-testid="compiler-run-btn"
          >
            <Play className="w-4 h-4 mr-2" />
            {running ? 'Running...' : 'Run'}
          </Button>
        </div>
      </header>

      <div className="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">
        <div className="flex-1 flex flex-col border-r border-border/50 min-h-0 overflow-hidden">
          <div className="px-2 py-1 border-b border-border/50 text-sm text-muted-foreground font-medium shrink-0">
            Code
          </div>
          <div className="flex-1 min-h-0 overflow-hidden">
            <Editor
              height="100%"
              language={LANG_EDITOR[language] || 'plaintext'}
              value={code}
              onChange={(v) => setCode(v ?? '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                padding: { top: 8 },
                scrollBeyondLastLine: false,
              }}
            />
          </div>
        </div>
        <div className="w-full md:w-96 flex flex-col border-t md:border-t-0 md:border-l border-border/50 shrink-0 min-h-0">
          <div className="border-b border-border/50 shrink-0">
            <div className="px-3 py-2 text-sm text-muted-foreground font-medium">Input (stdin)</div>
            <Textarea
              placeholder="Enter input for your program..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="min-h-[120px] rounded-none border-0 resize-none focus-visible:ring-0 font-mono text-sm"
              data-testid="compiler-input"
            />
          </div>
          <div className="flex-1 flex flex-col min-h-[120px] overflow-hidden">
            <div className="px-3 py-2 text-sm text-muted-foreground font-medium flex items-center justify-between shrink-0">
              <span>Output</span>
              {runtimeMs != null && (
                <span className="text-xs font-mono">{runtimeMs} ms</span>
              )}
            </div>
            <pre className="flex-1 p-3 overflow-auto text-sm font-mono bg-muted/20 border-t border-border/50 whitespace-pre-wrap break-words min-h-0">
              {error ? (
                <span className="text-destructive">{error}</span>
              ) : (
                output || (running ? 'Running...' : '')
              )}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompilerPage;
