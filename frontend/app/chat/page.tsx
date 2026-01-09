'use client';

import { useState, useEffect, useRef, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api';
import styles from './chat.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleLogout = () => {
    // Skip logout functionality for now
    handleClear();
  };

  const handleClear = () => {
    setMessages([]);
    setChatId(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await apiClient.sendMessage({
        message: userMessage,
        chat_id: chatId,
      });

      if (response.success) {
        setChatId(response.chat_id);
        setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to send message'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>🎓 EduBot</h1>
        <div className={styles.headerButtons}>
          <button onClick={handleClear} className={styles.clearBtn}>
            Clear
          </button>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            Logout
          </button>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.messages}>
          {messages.length === 0 && (
            <div className={styles.welcome}>
              <h2>Welcome to EduBot! 👋</h2>
              <p>Ask me anything about the university:</p>
              <ul>
                <li>How can I pay my tuition fees?</li>
                <li>Is November 1 a holiday?</li>
                <li>What is SQL and do we use it at the university?</li>
                <li>When is the fall semester tuition deadline?</li>
              </ul>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`${styles.message} ${
                msg.role === 'user' ? styles.userMessage : styles.assistantMessage
              }`}
            >
              <div className={styles.messageContent}>
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
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

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            disabled={loading}
            rows={3}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </main>
    </div>
  );
}
