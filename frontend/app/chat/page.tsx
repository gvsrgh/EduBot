'use client';

import { useState, useEffect, useRef, FormEvent, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import styles from './chat.module.css';
import { Chat } from '@/lib/types';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState<string | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [chatsLoading, setChatsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const editInputRef = useRef<HTMLInputElement>(null);
  const { user, logout } = useAuth();
  const router = useRouter();

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chats list when user is authenticated
  const loadChats = useCallback(async () => {
    if (!user) return;
    setChatsLoading(true);
    try {
      const chatList = await apiClient.getChats();
      setChats(chatList);
    } catch (err) {
      console.error('Failed to load chats:', err);
    } finally {
      setChatsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Focus edit input when editing
  useEffect(() => {
    if (editingChatId) {
      editInputRef.current?.focus();
    }
  }, [editingChatId]);

  const loadChatMessages = async (selectedChatId: string) => {
    if (!user) return;
    try {
      const data = await apiClient.getChatMessages(selectedChatId);
      const loadedMessages: Message[] = [];
      for (const msg of data.messages) {
        loadedMessages.push({ role: 'user', content: msg.human });
        loadedMessages.push({ role: 'assistant', content: msg.bot });
      }
      setMessages(loadedMessages);
      setChatId(selectedChatId);
    } catch (err) {
      console.error('Failed to load chat messages:', err);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setChatId(null);
  };

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

  const handleRename = async (targetChatId: string) => {
    if (!editTitle.trim()) {
      setEditingChatId(null);
      return;
    }
    try {
      await apiClient.renameChat(targetChatId, editTitle.trim());
      setChats(prev =>
        prev.map(c => (c.id === targetChatId ? { ...c, title: editTitle.trim() } : c))
      );
    } catch (err) {
      console.error('Failed to rename chat:', err);
    }
    setEditingChatId(null);
  };

  const handleArchive = async (targetChatId: string) => {
    try {
      await apiClient.archiveChat(targetChatId);
      setChats(prev => prev.filter(c => c.id !== targetChatId));
      if (chatId === targetChatId) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to archive chat:', err);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Use authenticated endpoint if logged in, public otherwise
      const response = user
        ? await apiClient.sendAuthMessage({ message: userMessage, chat_id: chatId })
        : await apiClient.sendMessage({ message: userMessage, chat_id: chatId });

      if (response.success) {
        setChatId(response.chat_id);
        setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
        // Refresh chat list after sending a message (new chat may have been created)
        if (user) {
          loadChats();
        }
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
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={styles.container}>
      {/* Sidebar - only for authenticated users */}
      {user && (
        <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
          <div className={styles.sidebarHeader}>
            <button onClick={handleNewChat} className={styles.newChatBtn}>
              + New Chat
            </button>
          </div>
          <div className={styles.chatList}>
            {chatsLoading ? (
              <p className={styles.sidebarEmpty}>Loading...</p>
            ) : chats.length === 0 ? (
              <p className={styles.sidebarEmpty}>No conversations yet</p>
            ) : (
              chats.map(chat => (
                <div
                  key={chat.id}
                  className={`${styles.chatItem} ${chatId === chat.id ? styles.chatItemActive : ''}`}
                  onClick={() => loadChatMessages(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <input
                      ref={editInputRef}
                      className={styles.editInput}
                      value={editTitle}
                      onChange={e => setEditTitle(e.target.value)}
                      onBlur={() => handleRename(chat.id)}
                      onKeyDown={e => {
                        if (e.key === 'Enter') handleRename(chat.id);
                        if (e.key === 'Escape') setEditingChatId(null);
                      }}
                      onClick={e => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <div className={styles.chatItemContent}>
                        <span className={styles.chatItemTitle}>{chat.title}</span>
                        <span className={styles.chatItemDate}>{formatDate(chat.updated_at)}</span>
                      </div>
                      <div className={styles.chatItemActions}>
                        <button
                          className={styles.chatActionBtn}
                          title="Rename"
                          onClick={e => {
                            e.stopPropagation();
                            setEditingChatId(chat.id);
                            setEditTitle(chat.title);
                          }}
                        >
                          ✏️
                        </button>
                        <button
                          className={styles.chatActionBtn}
                          title="Delete"
                          onClick={e => {
                            e.stopPropagation();
                            handleArchive(chat.id);
                          }}
                        >
                          🗑️
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </aside>
      )}

      {/* Main content */}
      <div className={styles.mainWrapper}>
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            {user && (
              <button
                onClick={() => setSidebarOpen(prev => !prev)}
                className={styles.toggleSidebarBtn}
                title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
              >
                {sidebarOpen ? '◀' : '▶'}
              </button>
            )}
            <div>
              <h1>🎓 EduBot+</h1>
              <span className={styles.username}>Welcome, {user ? user.username : 'Guest'}</span>
            </div>
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
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
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
    </div>
  );
}
