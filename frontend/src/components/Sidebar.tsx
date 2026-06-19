import React from "react";
import { Plus, Trash2, Moon, Sun, MessageSquare, Bot, X } from "lucide-react";

interface SidebarProps {
  sessions: string[];
  activeSession: string;
  onSelectSession: (id: string) => void;
  onAddSession: () => void;
  onDeleteSession: (id: string) => void;
  darkMode: boolean;
  onToggleTheme: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSession,
  onSelectSession,
  onAddSession,
  onDeleteSession,
  darkMode,
  onToggleTheme,
  isOpen,
  onClose,
}) => {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-slate-900 text-slate-100 transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-auto ${
        isOpen ? "translate-x-0" : "-translate-x-0 -left-64 md:left-0"
      } flex flex-col border-r border-slate-800 shadow-xl`}
    >
      {/* Sidebar Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-violet-600 p-1.5">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <span className="text-lg font-semibold tracking-wider bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            RAG Chatbot
          </span>
        </div>
        {/* Mobile close button */}
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white md:hidden"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Action Buttons */}
      <div className="p-4">
        <button
          onClick={onAddSession}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 font-medium text-white shadow-lg shadow-violet-900/20 transition-all hover:bg-violet-500 active:scale-95"
        >
          <Plus className="h-5 w-5" />
          New Chat
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <p className="px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Conversations
        </p>
        {sessions.length === 0 ? (
          <p className="px-3 py-4 text-sm text-slate-500 italic">No recent chats</p>
        ) : (
          sessions.map((session) => {
            const isActive = session === activeSession;
            return (
              <div
                key={session}
                className={`group flex items-center justify-between rounded-xl px-3 py-2.5 transition-all cursor-pointer ${
                  isActive
                    ? "bg-slate-800 text-violet-400 border border-slate-700/50"
                    : "hover:bg-slate-850 text-slate-300 hover:text-white"
                }`}
                onClick={() => {
                  onSelectSession(session);
                  onClose(); // auto close sidebar on mobile
                }}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <MessageSquare className={`h-4 w-4 shrink-0 ${isActive ? "text-violet-400" : "text-slate-500"}`} />
                  <span className="truncate text-sm font-medium">
                    {session === "default" ? "Default Workspace" : `Session: ${session}`}
                  </span>
                </div>
                {/* Delete session button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session);
                  }}
                  className="rounded-lg p-1 text-slate-500 opacity-0 group-hover:opacity-100 hover:bg-slate-750 hover:text-red-400 transition-opacity"
                  title="Delete Conversation"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Sidebar Footer / Settings */}
      <div className="p-4 border-t border-slate-850 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-400">Theme</span>
          <button
            onClick={onToggleTheme}
            className="flex items-center gap-2 rounded-xl bg-slate-800 px-3 py-2 text-sm font-medium text-slate-200 border border-slate-700/35 hover:bg-slate-750 hover:text-white transition-colors"
          >
            {darkMode ? (
              <>
                <Sun className="h-4 w-4 text-amber-400" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon className="h-4 w-4 text-violet-400" />
                <span>Dark</span>
              </>
            )}
          </button>
        </div>
      </div>
    </aside>
  );
};
