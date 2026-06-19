import React, { useRef, useEffect } from "react";
import { Send, Sparkles, MessageSquare, Menu } from "lucide-react";
import { MessageItem } from "./MessageItem";
import type { MessageHistoryItem } from "../services/api";

interface ChatWindowProps {
  messages: MessageHistoryItem[];
  currentContext: string;
  input: string;
  setInput: (val: string) => void;
  onSendMessage: (e: React.FormEvent) => void;
  isLoading: boolean;
  isStreaming: boolean;
  setIsStreaming: (val: boolean) => void;
  onClearHistory: () => void;
  onOpenSidebar: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  currentContext,
  input,
  setInput,
  onSendMessage,
  isLoading,
  isStreaming,
  setIsStreaming,
  onClearHistory,
  onOpenSidebar,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Smooth scroll to bottom on message list update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-1 flex-col bg-slate-50 dark:bg-slate-900 transition-colors h-full overflow-hidden">
      {/* Chat Window Header */}
      <header className="flex h-16 items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 shadow-sm transition-colors shrink-0">
        <div className="flex items-center gap-3">
          {/* Mobile hamburger menu */}
          <button
            onClick={onOpenSidebar}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900 dark:text-slate-400 md:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-violet-500" />
            <span className="font-semibold text-slate-800 dark:text-slate-100">
              Active Conversation
            </span>
          </div>
        </div>

        {/* Clear memory button */}
        {messages.length > 0 && (
          <button
            onClick={onClearHistory}
            className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs font-semibold text-red-500 dark:text-red-400 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            Reset Memory
          </button>
        )}
      </header>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto bg-slate-50/50 dark:bg-slate-900/30">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center p-6 text-center">
            <div className="rounded-full bg-violet-100 dark:bg-violet-950/40 p-4 text-violet-600 dark:text-violet-400">
              <Sparkles className="h-10 w-10 animate-pulse" />
            </div>
            <h2 className="mt-4 text-xl font-bold text-slate-800 dark:text-slate-200">
              Retrieval-Augmented Chatbot
            </h2>
            <p className="mt-2 max-w-sm text-sm text-slate-555 dark:text-slate-450 leading-relaxed">
              Ask anything! The bot will retrieve relevant details from files and contextually build answers with Gemini.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2.5">
              <span className="rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 px-3.5 py-1.5 text-xs text-slate-600 dark:text-slate-300">
                📚 PDFs & Documents context
              </span>
              <span className="rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 px-3.5 py-1.5 text-xs text-slate-600 dark:text-slate-300">
                🧠 Short & Long-term memory
              </span>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {messages.map((msg, index) => {
              const isLastMsg = index === messages.length - 1;
              return (
                <MessageItem
                  key={index}
                  role={msg.role}
                  content={msg.content}
                  // Associate the RAG context with the assistant's final response
                  context={!isLastMsg && msg.role === "assistant" ? undefined : (msg.role === "assistant" ? currentContext : undefined)}
                />
              );
            })}

            {/* Typing Indicator */}
            {isLoading && (
              <div className="flex w-full gap-4 bg-white dark:bg-slate-850/50 p-6">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-violet-500">
                  <Sparkles className="h-5 w-5 animate-spin" />
                </div>
                <div className="flex flex-col gap-1.5 mt-1.5">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-450">
                    Assistant
                  </span>
                  <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-4 py-3.5 rounded-2xl w-24">
                    <span className="h-2 w-2 rounded-full bg-slate-400 dark:bg-slate-500 animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="h-2 w-2 rounded-full bg-slate-400 dark:bg-slate-500 animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="h-2 w-2 rounded-full bg-slate-400 dark:bg-slate-500 animate-bounce"></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input panel container */}
      <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4 transition-colors shrink-0">
        <form onSubmit={onSendMessage} className="mx-auto max-w-4xl space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isLoading ? "Please wait..." : "Type your message here..."}
              disabled={isLoading}
              className="flex-1 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-4 py-3.5 text-sm text-slate-800 dark:text-slate-100 placeholder-slate-450 shadow-inner focus:border-violet-500 focus:outline-none dark:focus:border-violet-500 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-violet-600 text-white shadow-lg shadow-violet-900/20 hover:bg-violet-500 active:scale-95 transition-all disabled:opacity-40"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>

          {/* Streaming Toggle Switch */}
          <div className="flex items-center gap-2.5 px-1.5 text-xs text-slate-500 dark:text-slate-400">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={isStreaming}
                onChange={(e) => setIsStreaming(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-200 dark:bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-violet-600"></div>
              <span className="ml-2 font-medium">Stream Responses (SSE)</span>
            </label>
          </div>
        </form>
      </footer>
    </div>
  );
};
