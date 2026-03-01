'use client';

import { useState, useEffect, useRef, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import styles from './chat.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  status?: string;   // tool-use status (e.g. "Searching...")
  streaming?: boolean; // true while still receiving tokens
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleLogout = () => {
    logout();
  };

  const handleLogin = () => {
    router.push('/login');
  };

  const handleClear = () => {
    setMessages([]);
    setChatId(null);
  };

  const handleSettings = () => {
    router.push('/settings');
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    // Authenticated users → try streaming; unauthenticated → non-streaming
    if (user) {
      // Add a placeholder assistant message that tokens will stream into
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '', streaming: true },
      ]);

      try {
        await apiClient.streamMessage(
          { message: userMessage, chat_id: chatId },
          {
            onToken(token) {
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  updated[updated.length - 1] = {
                    ...last,
                    content: last.content + token,
                  };
                }
                return updated;
              });
            },
            onStatus(status) {
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  updated[updated.length - 1] = { ...last, status };
                }
                return updated;
              });
            },
            onComplete(newChatId) {
              setChatId(newChatId);
              // Mark streaming done
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  updated[updated.length - 1] = {
                    ...last,
                    streaming: false,
                    status: undefined,
                  };
                }
                return updated;
              });
              loadChats();
            },
            onError(errMsg) {
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  updated[updated.length - 1] = {
                    ...last,
                    content: last.content || `Error: ${errMsg}`,
                    streaming: false,
                    status: undefined,
                  };
                }
                return updated;
              });
            },
          },
        );
      } catch (err) {
        // Streaming failed — fall back to non-streaming
        setMessages(prev => prev.filter(m => !(m.role === 'assistant' && m.streaming)));
        try {
          const response = await apiClient.sendAuthMessage({
            message: userMessage,
            chat_id: chatId,
          });
          if (response.success) {
            setChatId(response.chat_id);
            setMessages(prev => [
              ...prev,
              { role: 'assistant', content: response.message },
            ]);
            loadChats();
          } else {
            setMessages(prev => [
              ...prev,
              { role: 'assistant', content: 'Sorry, I was unable to process your request. Please try again.' },
            ]);
          }
        } catch (fallbackErr) {
          setMessages(prev => [
            ...prev,
            {
              role: 'assistant',
              content: `Error: ${fallbackErr instanceof Error ? fallbackErr.message : 'Failed to send message'}`,
            },
          ]);
        }
      } finally {
        setLoading(false);
      }
    } else {
      // Unauthenticated — non-streaming
      try {
        const response = await apiClient.sendMessage({
          message: userMessage,
          chat_id: chatId,
        });
        if (response.success) {
          setChatId(response.chat_id);
          setMessages(prev => [
            ...prev,
            { role: 'assistant', content: response.message },
          ]);
        } else {
          setMessages(prev => [
            ...prev,
            { role: 'assistant', content: 'Sorry, I was unable to process your request. Please try again.' },
          ]);
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
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1>🎓 EduBot+</h1>
          <span className={styles.username}>Welcome, {user ? user.username : 'Guest'}</span>
        </div>
        <div className={styles.headerButtons}>
          <button onClick={handleClear} className={styles.clearBtn}>
            Clear
          </button>
          {user && (
            <button onClick={handleSettings} className={styles.settingsBtn}>
              ⚙️ Settings
            </button>
          )}
          {user ? (
            <button onClick={handleLogout} className={styles.logoutBtn}>
              Logout
            </button>
          ) : (
            <button onClick={handleLogin} className={styles.logoutBtn}>
              Login
            </button>
          )}
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.messages}>
          {messages.length === 0 && (
            <div className={styles.welcome}>
              <h2>Welcome to EduBot+! 👋</h2>
              <p>Ask me anything about the university:</p>
              <ul>
                <li>What is the B.Tech fee structure for management and convenor quota?</li>
                <li>When is Republic Day in 2026?</li>
                <li>What are the exam dates for I B.Tech first semester?</li>
                <li>When does the IV B.Tech second semester start?</li>
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

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.message} ${
                  msg.role === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageContent}>
                  {msg.role === 'assistant' ? (
                    <>
                      {msg.status && (
                        <div className={styles.streamStatus}>
                          🔍 {msg.status}
                        </div>
                      )}
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {msg.streaming && <span className={styles.streamCursor}>▊</span>}
                    </>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            </div>
          )}

            {loading && !messages.some(m => m.streaming) && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.messageContent}>
                  <span className={styles.typing}>Thinking...</span>
                </div>
              </div>
            )}

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
