"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getApiBase } from "../../lib/api-base";
import styles from "./widget.module.css";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
}

const API_BASE = getApiBase();

const SAMPLE_QUESTIONS = [
  "What are the B.Tech programs offered?",
  "What is the fee structure?",
  "When is the next holiday?",
];

export default function WidgetPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [greeting, setGreeting] = useState("");
  const [isEmbed, setIsEmbed] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const g = params.get("greeting");
    const embed = params.get("embed");
    if (g) setGreeting(g);
    if (embed === "1") setIsEmbed(true);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const formatAssistantText = (text: string) => {
    return text
      .replace(/([.!?])([A-Z])/g, "$1 $2")
      .replace(/([a-zA-Z])(\d+\.)/g, "$1 $2");
  };

  async function sendMessage(text: string) {
    if (!text.trim() || loading) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/widget/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (res.status === 429) {
        const err = await res.json();
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: "assistant", text: err.detail || "Too many requests. Please wait." },
        ]);
        return;
      }

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (data.session_id) setSessionId(data.session_id);

      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: "assistant", text: data.message },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          text: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage(input.trim());
  }

  function handleClose() {
    if (isEmbed && window.parent !== window) {
      window.parent.postMessage("edubot-widget-close", "*");
    }
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerInfo}>
          <div className={styles.headerDot} />
          <span className={styles.headerTitle}>🎓 EduBot+</span>
        </div>
        {isEmbed && (
          <button className={styles.closeBtn} onClick={handleClose} aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className={styles.messages}>
        {messages.length === 0 && !loading && (
          <div className={styles.welcome}>
            <h3>{greeting || "Welcome to EduBot+! 👋"}</h3>
            <p>Ask me anything about the university:</p>
            <ul>
              {SAMPLE_QUESTIONS.map((q, i) => (
                <li key={i} onClick={() => sendMessage(q)}>{q}</li>
              ))}
            </ul>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${
              msg.role === "user" ? styles.userMessage : styles.assistantMessage
            }`}
          >
            <div className={styles.messageContent}>
              {msg.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{formatAssistantText(msg.text)}</ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className={`${styles.message} ${styles.assistantMessage}`}>
            <div className={styles.messageContent}>
              <span className={styles.typing}>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form className={styles.inputBar} onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className={styles.input}
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={2000}
          disabled={loading}
          autoFocus
        />
        <button
          className={styles.sendBtn}
          type="submit"
          disabled={loading || !input.trim()}
          aria-label="Send"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
}
