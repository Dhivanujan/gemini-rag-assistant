import React, { useState } from "react";
import { Copy, Check, ChevronDown, ChevronUp, User, Bot, BookOpen } from "lucide-react";

interface MessageItemProps {
  role: "user" | "assistant";
  content: string;
  context?: string;
}

export const MessageItem: React.FC<MessageItemProps> = ({ role, content, context }) => {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const parseMarkdown = (text: string) => {
    if (!text) return null;

    // Split text by code blocks
    const parts = text.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      // Code block parsing
      if (part.startsWith("```") && part.endsWith("```")) {
        const lines = part.split("\n");
        const language = lines[0].replace("```", "").trim() || "code";
        const code = lines.slice(1, -1).join("\n");

        return (
          <div key={index} className="my-3 overflow-hidden rounded-xl border border-slate-700/50 bg-slate-950 font-mono text-sm shadow-md">
            <div className="flex items-center justify-between bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-400">
              <span className="uppercase tracking-wider">{language}</span>
              <button
                onClick={() => handleCopy(code)}
                className="flex items-center gap-1 hover:text-slate-200 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="overflow-x-auto p-4 text-slate-300">
              <code>{code}</code>
            </pre>
          </div>
        );
      }

      // Inline code, list items, bold tags, and paragraph parsing
      const subLines = part.split("\n");
      return (
        <div key={index} className="space-y-2">
          {subLines.map((line, lIdx) => {
            let processedLine = line;

            // Handle lists
            const isBullet = processedLine.trim().startsWith("- ") || processedLine.trim().startsWith("* ");
            const isNumbered = /^\d+\.\s/.test(processedLine.trim());

            if (isBullet) {
              processedLine = processedLine.replace(/^[\s]*[-*]\s/, "");
            } else if (isNumbered) {
              processedLine = processedLine.replace(/^[\s]*\d+\.\s/, "");
            }

            // Inline code `code`
            const codeParts = processedLine.split(/(`[^`]+`)/g);
            const lineContent = codeParts.map((subPart, spIdx) => {
              if (subPart.startsWith("`") && subPart.endsWith("`")) {
                return (
                  <code key={spIdx} className="rounded bg-slate-800 dark:bg-slate-900 border border-slate-700/30 px-1.5 py-0.5 font-mono text-xs text-rose-400 font-semibold">
                    {subPart.slice(1, -1)}
                  </code>
                );
              }

              // Bold **text**
              const boldParts = subPart.split(/(\*\*[^*]+\*\*)/g);
              return boldParts.map((bPart, bpIdx) => {
                if (bPart.startsWith("**") && bPart.endsWith("**")) {
                  return (
                    <strong key={bpIdx} className="font-semibold text-slate-900 dark:text-slate-100">
                      {bPart.slice(2, -2)}
                    </strong>
                  );
                }
                return bPart;
              });
            });

            if (isBullet) {
              return (
                <ul key={lIdx} className="list-disc pl-5 space-y-1 text-slate-700 dark:text-slate-350">
                  <li className="leading-relaxed">{lineContent}</li>
                </ul>
              );
            }

            if (isNumbered) {
              return (
                <ol key={lIdx} className="list-decimal pl-5 space-y-1 text-slate-700 dark:text-slate-350">
                  <li className="leading-relaxed">{lineContent}</li>
                </ol>
              );
            }

            // Simple line break for empty lines
            if (!processedLine.trim()) {
              return <div key={lIdx} className="h-2" />;
            }

            return (
              <p key={lIdx} className="leading-relaxed text-slate-700 dark:text-slate-300">
                {lineContent}
              </p>
            );
          })}
        </div>
      );
    });
  };

  const isUser = role === "user";

  return (
    <div className={`flex w-full gap-4 p-4 md:p-6 transition-all ${isUser ? "bg-slate-50 dark:bg-slate-850/20" : "bg-white dark:bg-slate-850/50"}`}>
      {/* Avatar icon */}
      <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl shadow-md border ${
        isUser
          ? "bg-gradient-to-tr from-violet-500 to-indigo-500 border-indigo-400/30 text-white"
          : "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-violet-600 dark:text-violet-400"
      }`}>
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      {/* Main message card */}
      <div className="flex-1 overflow-hidden">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {isUser ? "You" : "Assistant"}
        </span>

        {/* Message body */}
        <div className="mt-2 text-sm md:text-base space-y-2 whitespace-pre-wrap">
          {parseMarkdown(content)}
        </div>

        {/* RAG Context Accordion for Assistant */}
        {!isUser && context && (
          <div className="mt-4 border-t border-slate-200 dark:border-slate-800 pt-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-350 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              <BookOpen className="h-3.5 w-3.5 text-violet-500" />
              <span>{showSources ? "Hide Sources" : "View Sources"}</span>
              {showSources ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            </button>

            {showSources && (
              <div className="mt-2.5 overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 p-4 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                <p className="font-semibold text-slate-650 dark:text-slate-300 mb-1.5 uppercase tracking-wide text-[10px]">
                  Retrieved Knowledge Context
                </p>
                <div className="whitespace-pre-wrap font-mono">{context}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
