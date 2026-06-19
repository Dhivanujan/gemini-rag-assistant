import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface MessageHistoryItem {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  question: string;
  context: string;
  answer: string;
  session_id: string;
}

export const getHistory = async (sessionId: string) => {
  const response = await api.get<{ history: MessageHistoryItem[] }>(`/history/${sessionId}`);
  return response.data.history;
};

export const deleteHistory = async (sessionId: string) => {
  const response = await api.delete<{ status: string; message: string }>(`/history/${sessionId}`);
  return response.data;
};

export const postChatNonStream = async (message: string, sessionId: string) => {
  const response = await api.post<ChatResponse>("/chat", {
    message,
    session_id: sessionId,
    stream: false,
  });
  return response.data;
};

export const streamChat = async (
  message: string,
  sessionId: string,
  onChunk: (text: string) => void,
  onContext: (context: string) => void,
  onDone: () => void,
  onError: (err: any) => void
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No response body stream found.");
    }

    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      // Keep any remaining partial lines in the buffer
      buffer = lines.pop() || "";

      for (const line of lines) {
        const cleanLine = line.trim();
        if (!cleanLine) continue;

        if (cleanLine.startsWith("data: ")) {
          const dataStr = cleanLine.substring(6);
          try {
            const payload = JSON.parse(dataStr);
            if (payload.type === "context") {
              onContext(payload.context);
            } else if (payload.type === "content") {
              onChunk(payload.content);
            } else if (payload.type === "done") {
              onDone();
            } else if (payload.type === "error") {
              onError(new Error(payload.error));
            }
          } catch (e) {
            console.error("Error parsing SSE chunk:", e);
          }
        }
      }
    }
  } catch (error) {
    onError(error);
  }
};
