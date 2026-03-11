import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';

const CODE_BLOCK_REGEX = /```(\w*)\n?([\s\S]*?)```/g;

function CodeBlock({ language, code }) {
  const [copied, setCopied] = useState(false);
  const lang = (language || 'text').toLowerCase();
  const codeStr = typeof code === 'string' ? code : String(code ?? '');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeStr);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_) {}
  };

  return (
    <div className="relative group my-2 rounded-lg overflow-hidden border border-border/60 bg-[#1e1e1e]">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-border/60 bg-[#252526]">
        <span className="text-xs text-muted-foreground font-mono">{lang || 'plaintext'}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="p-1.5 rounded hover:bg-white/10 text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Copy code"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </div>
      <SyntaxHighlighter
        language={lang}
        style={oneDark}
        customStyle={{ margin: 0, padding: '12px 16px', fontSize: '13px', background: 'transparent' }}
        codeTagProps={{ style: { fontFamily: 'var(--font-mono), monospace' } }}
        showLineNumbers={false}
        PreTag="div"
      >
        {codeStr.trim()}
      </SyntaxHighlighter>
    </div>
  );
}

function parseContent(text) {
  const str = text == null ? '' : typeof text === 'string' ? text : String(text);
  if (!str) return [{ type: 'text', value: '' }];
  const parts = [];
  let lastIndex = 0;
  let match;
  const re = new RegExp(CODE_BLOCK_REGEX.source, 'g');
  while ((match = re.exec(str)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: str.slice(lastIndex, match.index) });
    }
    parts.push({ type: 'code', language: match[1] || '', value: match[2] });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < str.length) {
    parts.push({ type: 'text', value: str.slice(lastIndex) });
  }
  if (parts.length === 0) parts.push({ type: 'text', value: str });
  return parts;
}

export default function CoachMessageContent({ content }) {
  const parts = parseContent(content);
  return (
    <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
      {parts.map((part, i) => {
        if (part.type === 'text') {
          const value = part.value || '';
          return (
            <span key={i} className="inline">
              {value.split('\n').map((line, j) => (
                <React.Fragment key={j}>
                  {j > 0 && <br />}
                  {line}
                </React.Fragment>
              ))}
            </span>
          );
        }
        return <CodeBlock key={i} language={part.language} code={part.value} />;
      })}
    </div>
  );
}
