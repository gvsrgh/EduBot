'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import styles from './settings.module.css';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001/api';

interface ProviderSettings {
  ai_provider: string;
  available_providers: {
    [key: string]: boolean;
  };
}

interface Settings {
  id: number;
  ai_provider: string;
  deny_words: string;
  max_tokens: number;
  temperature: string;
  updated_at: string;
}

export default function SettingsPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [providerSettings, setProviderSettings] = useState<ProviderSettings | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  
  const [formData, setFormData] = useState({
    ai_provider: 'ollama',
  });
  
  const [apiKeys, setApiKeys] = useState({
    openai_key: '',
    openai_model: 'gpt-4',
    gemini_key: '',
    gemini_model: 'gemini-2.0-flash-exp',
    ollama_url: 'http://localhost:11434',
    ollama_model: 'llama3.1:8b',
  });
  
  const [ollamaTestStatus, setOllamaTestStatus] = useState('');
  const [testingOllama, setTestingOllama] = useState(false);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      // Load provider settings
      const providerResponse = await fetch(`${API_BASE}/settings/provider`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (providerResponse.ok) {
        const providerData = await providerResponse.json();
        setProviderSettings(providerData);
      }

      // Load general settings
      const settingsResponse = await fetch(`${API_BASE}/settings/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        setSettings(settingsData);
        setFormData({
          ai_provider: settingsData.ai_provider,
        });
      } else if (settingsResponse.status === 403) {
        setError('Access denied. Admin privileges with @pvpsiddhartha.ac.in domain required.');
        setTimeout(() => router.push('/chat'), 2000);
      }
    } catch (err) {
      setError('Failed to load settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Check if user is logged in
    if (!user) {
      router.push('/login');
      return;
    }
    
    // Load API keys from localStorage
    const savedKeys = localStorage.getItem('edubot_api_keys');
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys));
      } catch (e) {
        console.error('Failed to parse saved API keys');
      }
    }
    
    loadSettings();
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${API_BASE}/settings/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const updatedSettings = await response.json();
        setSettings(updatedSettings);
        setSuccess('Settings updated successfully!');
        
        // Reload provider settings to get updated available providers
        const providerResponse = await fetch(`${API_BASE}/settings/provider`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (providerResponse.ok) {
          const providerData = await providerResponse.json();
          setProviderSettings(providerData);
        }
      } else if (response.status === 403) {
        setError('Access denied. Admin privileges with @pvpsiddhartha.ac.in domain required.');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update settings');
      }
    } catch (err) {
      setError('An error occurred while saving settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };
  
  const testOllamaConnection = async () => {
    setTestingOllama(true);
    setOllamaTestStatus('');
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const response = await fetch(`${API_BASE}/settings/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          provider: 'ollama',
          ollama_url: apiKeys.ollama_url
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setOllamaTestStatus(`✓ ${result.message}. ${result.details || ''}`);
        } else {
          setOllamaTestStatus(`✗ ${result.message}. ${result.details || ''}`);
        }
      } else {
        setOllamaTestStatus('✗ Connection test failed');
      }
    } catch (err) {
      setOllamaTestStatus('✗ Cannot connect. Make sure Ollama is running.');
    } finally {
      setTestingOllama(false);
    }
  };
  
  const testOpenAIConnection = async () => {
    if (!apiKeys.openai_key) {
      setError('Please enter an OpenAI API key first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const response = await fetch(`${API_BASE}/settings/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          provider: 'openai',
          api_key: apiKeys.openai_key
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setSuccess(`✓ ${result.message}. ${result.details || ''}`);
        } else {
          setError(`✗ ${result.message}. ${result.details || ''}`);
        }
      } else {
        setError('Connection test failed');
      }
    } catch (err) {
      setError('Cannot connect to OpenAI');
    } finally {
      setLoading(false);
    }
  };
  
  const testGeminiConnection = async () => {
    if (!apiKeys.gemini_key) {
      setError('Please enter a Gemini API key first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const response = await fetch(`${API_BASE}/settings/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          provider: 'gemini',
          api_key: apiKeys.gemini_key
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setSuccess(`✓ ${result.message}. ${result.details || ''}`);
        } else {
          setError(`✗ ${result.message}. ${result.details || ''}`);
        }
      } else {
        setError('Connection test failed');
      }
    } catch (err) {
      setError('Cannot connect to Gemini');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading settings...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Settings</h1>
        <p className={styles.subtitle}>
          Configure EduBot+ application settings and preferences
        </p>
      </div>

      {error && <div className={styles.error}>{error}</div>}
      {success && <div className={styles.success}>{success}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* AI Provider & Configuration Section */}
        <section className={styles.section}>
          <h2>AI Provider & Configuration</h2>
          <p className={styles.description}>
            Select your AI provider and configure the necessary credentials.
          </p>
          
          <div className={styles.privacyNotice}>
            <span className={styles.lockIcon}>🔒</span>
            <div>
              <strong>Privacy Notice:</strong> API keys are stored locally in your browser only. 
              We do NOT store your API keys on our servers.
            </div>
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="ai_provider">Select Provider</label>
            <select
              id="ai_provider"
              value={formData.ai_provider}
              onChange={(e) => setFormData({ ...formData, ai_provider: e.target.value })}
              className={styles.select}
            >
              <option value="ollama">Local Ollama (Recommended)</option>
              <option value="openai">OpenAI GPT-4</option>
              <option value="gemini">Google Gemini</option>
              <option value="auto">Auto (University-Provided API with Fallback)</option>
            </select>
          </div>
          
          {/* Conditional API Key Inputs */}
          {formData.ai_provider === 'openai' && (
            <>
              <div className={styles.formGroup}>
                <label htmlFor="openai_key">OpenAI API Key</label>
                <input
                  type="password"
                  id="openai_key"
                  value={apiKeys.openai_key}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, openai_key: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  placeholder="sk-..." 
                  className={styles.input}
                />
                <small className={styles.hint}>
                  Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI Platform</a>
                </small>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="openai_model">OpenAI Model</label>
                <select
                  id="openai_model"
                  value={apiKeys.openai_model}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, openai_model: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  className={styles.select}
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                </select>
                <small className={styles.hint}>
                  Select the OpenAI model to use
                </small>
              </div>
              <div className={styles.formGroup}>
                <button
                  type="button"
                  onClick={testOpenAIConnection}
                  disabled={loading || !apiKeys.openai_key}
                  className={styles.testButton}
                >
                  {loading ? 'Testing...' : '🔍 Test Connection'}
                </button>
              </div>
            </>
          )}
          
          {formData.ai_provider === 'gemini' && (
            <>
              <div className={styles.formGroup}>
                <label htmlFor="gemini_key">Google Gemini API Key</label>
                <input
                  type="password"
                  id="gemini_key"
                  value={apiKeys.gemini_key}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, gemini_key: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  placeholder="AI..." 
                  className={styles.input}
                />
                <small className={styles.hint}>
                  Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
                </small>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="gemini_model">Gemini Model</label>
                <select
                  id="gemini_model"
                  value={apiKeys.gemini_model}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, gemini_model: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  className={styles.select}
                >
                  <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Experimental)</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  <option value="gemini-pro">Gemini Pro</option>
                </select>
                <small className={styles.hint}>
                  Select the Gemini model to use
                </small>
              </div>
              <div className={styles.formGroup}>
                <button
                  type="button"
                  onClick={testGeminiConnection}
                  disabled={loading || !apiKeys.gemini_key}
                  className={styles.testButton}
                >
                  {loading ? 'Testing...' : '🔍 Test Connection'}
                </button>
              </div>
            </>
          )}
          
          {formData.ai_provider === 'ollama' && (
            <>
              <div className={styles.formGroup}>
                <label htmlFor="ollama_url">Ollama Server URL</label>
                <input
                  type="text"
                  id="ollama_url"
                  value={apiKeys.ollama_url}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, ollama_url: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  placeholder="http://localhost:11434" 
                  className={styles.input}
                />
                <small className={styles.hint}>
                  URL of your local Ollama instance. Default: http://localhost:11434
                </small>
              </div>
              
              <div className={styles.formGroup}>
                <label htmlFor="ollama_model">Ollama Model</label>
                <input
                  type="text"
                  id="ollama_model"
                  value={apiKeys.ollama_model}
                  onChange={(e) => {
                    const newKeys = { ...apiKeys, ollama_model: e.target.value };
                    setApiKeys(newKeys);
                    localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
                  }}
                  placeholder="llama3.1:8b" 
                  className={styles.input}
                />
                <small className={styles.hint}>
                  Model name (e.g., llama3.1:8b, llama2, mistral). Use 'ollama list' to see available models.
                </small>
              </div>
              
              <div className={styles.formGroup}>
                <button
                  type="button"
                  onClick={testOllamaConnection}
                  disabled={testingOllama}
                  className={styles.testButton}
                >
                  {testingOllama ? 'Testing...' : '🔍 Test Connection'}
                </button>
                {ollamaTestStatus && (
                  <div className={ollamaTestStatus.startsWith('✓') ? styles.testSuccess : styles.testError}>
                    {ollamaTestStatus}
                  </div>
                )}
              </div>
            </>
          )}
          
          {providerSettings && (
            <div className={styles.providerStatus}>
              <p><strong>Current Active Provider:</strong> {providerSettings.ai_provider}</p>
              <p><strong>System Status:</strong></p>
                <ul>
                  {Object.entries(providerSettings.available_providers).map(([provider, available]) => (
                    <li key={provider} className={available ? styles.available : styles.unavailable}>
                      {provider}: {available ? '✓ Available' : '✗ Unavailable'}
                    </li>
                  ))}
                </ul>
            </div>
          )}
        </section>

        {/* Last Updated Info */}
        {settings && (
          <div className={styles.info}>
            Last updated: {new Date(settings.updated_at).toLocaleString()}
          </div>
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button
            type="button"
            onClick={() => router.push('/chat')}
            className={styles.cancelButton}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className={styles.saveButton}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
}
