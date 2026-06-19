import React, { useState, useEffect } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import {
  getHistory,
  deleteHistory,
  postChatNonStream,
  streamChat,
} from "./services/api";
import type { MessageHistoryItem } from "./services/api";

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<string[]>(["default"]);
  const [activeSession, setActiveSession] = useState<string>("default");
  const [messages, setMessages] = useState<MessageHistoryItem[]>([]);
  const [currentContext, setCurrentContext] = useState<string>("");
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(true); // Default to streaming
  const [darkMode, setDarkMode] = useState<boolean>(true); // Default to premium dark mode
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  // Initialize theme and load sessions from localStorage if available
  useEffect(() => {
    // Default to dark mode if no local preference exists
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme ? savedTheme === "dark" : true;
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    const savedSessions = localStorage.getItem("chat_sessions");
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setSessions(parsed);
          // Auto select first session
          setActiveSession(parsed[0]);
        }
      } catch (e) {
        console.error("Error loading sessions from local storage:", e);
      }
    }
  }, []);

  // Sync sessions to localStorage
  useEffect(() => {
    localStorage.setItem("chat_sessions", JSON.stringify(sessions));
  }, [sessions]);

  // Load session history when switching sessions
  useEffect(() => {
    const loadSessionHistory = async () => {
      setIsLoading(true);
      setCurrentContext("");
      try {
        const history = await getHistory(activeSession);
        setMessages(history);
      } catch (e) {
        console.error("Failed to load chat history:", e);
      } finally {
        setIsLoading(false);
      }
    };
    loadSessionHistory();
  }, [activeSession]);

  const handleToggleTheme = () => {
    const nextDark = !darkMode;
    setDarkMode(nextDark);
    localStorage.setItem("theme", nextDark ? "dark" : "light");
    if (nextDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const handleAddSession = () => {
    const name = prompt("Enter a name for the new chat session:");
    if (!name) return;

    // Sanitize session id to contain only alphanumeric or underscores
    const sanitized = name
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9-_]/g, "_");

    if (!sanitized) {
      alert("Invalid session name!");
      return;
    }

    if (sessions.includes(sanitized)) {
      alert("Session name already exists!");
      return;
    }

    const nextSessions = [...sessions, sanitized];
    setSessions(nextSessions);
    setActiveSession(sanitized);
  };

  const handleDeleteSession = async (id: string) => {
    if (id === "default" && sessions.length === 1) {
      alert("Cannot delete the only remaining session!");
      return;
    }

    if (!confirm(`Are you sure you want to delete session "${id}"?`)) return;

    try {
      await deleteHistory(id);
      const nextSessions = sessions.filter((s) => s !== id);
      setSessions(nextSessions);

      if (activeSession === id) {
        setActiveSession(nextSessions[0] || "default");
      }
    } catch (e) {
      console.error("Failed to delete session history:", e);
      alert("Failed to delete session!");
    }
  };

  const handleClearHistory = async () => {
    if (!confirm("Are you sure you want to clear this session's history?")) return;

    try {
      await deleteHistory(activeSession);
      setMessages([]);
      setCurrentContext("");
    } catch (e) {
      console.error("Failed to clear chat memory:", e);
      alert("Failed to clear history!");
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput("");
    setCurrentContext("");

    // Append user message immediately
    const userMsg: MessageHistoryItem = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);

    setIsLoading(true);

    if (isStreaming) {
      // Streaming mode
      try {
        // Pre-append empty assistant message that gets populated chunk by chunk
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        await streamChat(
          userText,
          activeSession,
          (chunk) => {
            // Update last message in the stream list
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === "assistant") {
                last.content += chunk;
              }
              return updated;
            });
          },
          (context) => {
            setCurrentContext(context);
          },
          () => {
            // Done streaming
            setIsLoading(false);
          },
          (err) => {
            console.error("Stream error:", err);
            alert(`Streaming failed: ${err.message || err}`);
            setIsLoading(false);
            // Remove the empty assistant message in case of instant error
            setMessages((prev) => prev.slice(0, -1));
          }
        );
      } catch (err: any) {
        console.error("Failed to fetch stream:", err);
        setIsLoading(false);
      }
    } else {
      // Non-streaming mode
      try {
        const data = await postChatNonStream(userText, activeSession);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.answer },
        ]);
        setCurrentContext(data.context);
      } catch (err: any) {
        console.error("API Error:", err);
        alert(`Request failed: ${err.response?.data?.detail || err.message}`);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors">
      {/* Sidebar navigation */}
      <Sidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={setActiveSession}
        onAddSession={handleAddSession}
        onDeleteSession={handleDeleteSession}
        darkMode={darkMode}
        onToggleTheme={handleToggleTheme}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main chat window workspace */}
      <ChatWindow
        messages={messages}
        currentContext={currentContext}
        input={input}
        setInput={setInput}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        isStreaming={isStreaming}
        setIsStreaming={setIsStreaming}
        onClearHistory={handleClearHistory}
        onOpenSidebar={() => setIsSidebarOpen(true)}
      />
    </div>
  );
};

export default App;
