"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant" | "system" | "developer";
  content: string;
};

async function streamChat(
  developerMessage: string,
  userMessage: string,
  model: string,
  onChunk: (text: string) => void
) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ developer_message: developerMessage, user_message: userMessage, model })
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => res.statusText);
    throw new Error(`Failed to connect to chat endpoint: ${res.status} ${res.statusText} - ${errorText}`);
  }

  if (!res.body) {
    throw new Error("No response body received from chat endpoint");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  // Stream chunks to UI
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [developerMessage, setDeveloperMessage] = useState(
    "You are a concise, helpful business assistant. Keep answers brief and clear."
  );
  const [model, setModel] = useState("gpt-4.1-mini");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    setError(null);
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg, { role: "assistant", content: "" }]);
    setInput("");
    setIsLoading(true);

    try {
      await streamChat(developerMessage, userMsg.content, model, (chunk) => {
        setMessages((prev) => {
          const next = [...prev];
          const lastIndex = next.length - 1;
          next[lastIndex] = { role: "assistant", content: (next[lastIndex]?.content ?? "") + chunk };
          return next;
        });
      });
    } catch (e: any) {
      setError(e?.message ?? "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a" }}>
      <header style={{ borderBottom: "1px solid #243047", background: "#0b1220" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: "linear-gradient(135deg,#60a5fa,#22d3ee)", boxShadow: "0 6px 20px rgba(34,211,238,.25)" }} />
            <div>
              <div style={{ color: "#e2e8f0", fontWeight: 700 }}>AI Chat</div>
              <div style={{ color: "#93a4bc", fontSize: 12 }}>FastAPI + Next.js</div>
            </div>
          </div>
          <div style={{ color: "#93a4bc", fontSize: 12 }}>Model</div>
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: 20, display: "grid", gridTemplateColumns: "320px 1fr", gap: 20 }}>
        <aside style={{ background: "#0b1220", border: "1px solid #243047", borderRadius: 12, padding: 16 }}>
          <div style={{ color: "#e2e8f0", fontWeight: 600, marginBottom: 12 }}>Session Settings</div>
          <label style={{ display: "block", color: "#9fb0c9", fontSize: 12, marginBottom: 6 }}>System/Developer Message</label>
          <textarea
            value={developerMessage}
            onChange={(e) => setDeveloperMessage(e.target.value)}
            style={{ width: "100%", height: 120, background: "#0f172a", color: "#dbeafe", border: "1px solid #243047", borderRadius: 8, padding: 10, outline: "none" }}
          />

          <label style={{ display: "block", color: "#9fb0c9", fontSize: 12, margin: "12px 0 6px" }}>Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)} style={{ width: "100%", background: "#0f172a", color: "#dbeafe", border: "1px solid #243047", borderRadius: 8, padding: 10 }}>
            <option value="gpt-4.1-mini">gpt-4.1-mini</option>
            <option value="gpt-4o-mini">gpt-4o-mini</option>
          </select>
        </aside>

        <section style={{ background: "#0b1220", border: "1px solid #243047", borderRadius: 12, display: "flex", flexDirection: "column", height: "calc(100vh - 140px)" }}>
          <div style={{ padding: 16, borderBottom: "1px solid #243047", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ color: "#e2e8f0", fontWeight: 600 }}>Conversation</div>
            {isLoading && <div style={{ color: "#93a4bc", fontSize: 12 }}>Streaming…</div>}
          </div>

          <div style={{ padding: 16, overflowY: "auto", flex: 1 }}>
            {messages.length === 0 && (
              <div style={{ color: "#9fb0c9", fontSize: 14 }}>Ask a question to get started.</div>
            )}
            <div style={{ display: "grid", gap: 12 }}>
              {messages.map((m, idx) => (
                <div key={idx} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                  <div
                    style={{
                      maxWidth: "75%",
                      whiteSpace: "pre-wrap",
                      background: m.role === "user" ? "#1d2a44" : "#0f172a",
                      color: "#e2e8f0",
                      border: "1px solid #243047",
                      padding: 12,
                      borderRadius: 10
                    }}
                  >
                    {m.content}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ padding: 16, borderTop: "1px solid #243047" }}>
            {error && (
              <div style={{ background: "#3f1d2a", color: "#fecaca", border: "1px solid #7f1d1d", padding: 8, borderRadius: 8, marginBottom: 8 }}>{error}</div>
            )}
            <div style={{ display: "flex", gap: 10 }}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message…"
                rows={2}
                style={{ flex: 1, background: "#0f172a", color: "#dbeafe", border: "1px solid #243047", borderRadius: 8, padding: 10, outline: "none" }}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                style={{
                  background: "linear-gradient(135deg,#60a5fa,#22d3ee)",
                  color: "#0b1220",
                  fontWeight: 700,
                  border: 0,
                  padding: "0 18px",
                  borderRadius: 8,
                  cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
                  opacity: isLoading || !input.trim() ? 0.6 : 1
                }}
              >
                Send
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}


