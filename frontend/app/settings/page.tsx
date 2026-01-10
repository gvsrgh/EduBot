'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import styles from './settings.module.css';

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
    deny_words: '',
    max_tokens: 2000,
    temperature: '0.7',
  });
  
  const [apiKeys, setApiKeys] = useState({
    openai_key: '',
    gemini_key: '',
    ollama_url: 'http://localhost:11434',
  });
  
  const [uploadData, setUploadData] = useState({
    category: 'academic',
    topic: '',
    file: null as File | null,
  });
  
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploading, setUploading] = useState(false);
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
      const providerResponse = await fetch('http://localhost:8000/settings/provider', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (providerResponse.ok) {
        const providerData = await providerResponse.json();
        setProviderSettings(providerData);
      }

      // Load general settings
      const settingsResponse = await fetch('http://localhost:8000/settings/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        setSettings(settingsData);
        setFormData({
          ai_provider: settingsData.ai_provider,
          deny_words: settingsData.deny_words,
          max_tokens: settingsData.max_tokens,
          temperature: settingsData.temperature,
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

      const response = await fetch('http://localhost:8000/settings/', {
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
        const providerResponse = await fetch('http://localhost:8000/settings/provider', {
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
  
  const handleFileUpload = async () => {
    if (!uploadData.file || !uploadData.topic.trim()) {
      setUploadStatus('Please select a file and enter a topic title');
      return;
    }
    
    setUploading(true);
    setUploadStatus('');
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const formData = new FormData();
      formData.append('file', uploadData.file);
      formData.append('category', uploadData.category);
      formData.append('topic', uploadData.topic);
      
      const response = await fetch('http://localhost:8000/settings/upload-content', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`✓ Successfully uploaded: ${result.filename}`);
        setUploadData({ category: 'academic', topic: '', file: null });
        // Reset file input
        const fileInput = document.getElementById('content-file') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else if (response.status === 403) {
        setUploadStatus('Access denied. Admin privileges required.');
      } else {
        const errorData = await response.json();
        setUploadStatus(`Error: ${errorData.detail || 'Upload failed'}`);
      }
    } catch (err) {
      setUploadStatus('An error occurred during upload');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };
  
  const testOllamaConnection = async () => {
    setTestingOllama(true);
    setOllamaTestStatus('');
    
    try {
      const response = await fetch(`${apiKeys.ollama_url}/api/tags`, {
        method: 'GET',
      });
      
      if (response.ok) {
        const data = await response.json();
        const modelCount = data.models?.length || 0;
        setOllamaTestStatus(`✓ Connected! Found ${modelCount} model(s)`);
      } else {
        setOllamaTestStatus('✗ Connection failed. Please check the URL.');
      }
    } catch (err) {
      setOllamaTestStatus('✗ Cannot connect. Make sure Ollama is running.');
    } finally {
      setTestingOllama(false);
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
          )}
          
          {formData.ai_provider === 'gemini' && (
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

        {/* Content Management Section - Only for @pvpsiddhartha.ac.in */}
        {user?.email?.endsWith('@pvpsiddhartha.ac.in') && (
          <section className={styles.section}>
            <h2>Content Management</h2>
            <p className={styles.description}>
              Upload university content to enhance the chatbot's knowledge base.
            </p>
            
            <div className={styles.formGroup}>
              <label htmlFor="category">Content Category</label>
              <select
                id="category"
                value={uploadData.category}
                onChange={(e) => setUploadData({ ...uploadData, category: e.target.value })}
                className={styles.select}
              >
                <option value="academic">Academic Information</option>
                <option value="administrative">Administrative Procedures</option>
                <option value="events">Events & Activities</option>
              </select>
              <small className={styles.hint}>
                Select the category that best describes your content
              </small>
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="topic">Topic Title</label>
              <input
                type="text"
                id="topic"
                value={uploadData.topic}
                onChange={(e) => setUploadData({ ...uploadData, topic: e.target.value })}
                placeholder="e.g., Admission Guidelines 2024"
                className={styles.input}
              />
              <small className={styles.hint}>
                Provide a descriptive title for this content
              </small>
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="file">Upload File</label>
              <input
                type="file"
                id="file"
                onChange={(e) => setUploadData({ ...uploadData, file: e.target.files?.[0] || null })}
                accept=".txt,.pdf,.doc,.docx"
                className={styles.fileInput}
              />
              <small className={styles.hint}>
                Supported formats: TXT, PDF, DOC, DOCX (Max 10MB)
              </small>
            </div>
            
            <button
              type="button"
              onClick={handleFileUpload}
              disabled={uploading || !uploadData.file || !uploadData.topic.trim()}
              className={styles.uploadButton}
            >
              {uploading ? '⏳ Uploading...' : '📤 Upload Content'}
            </button>
            
            {uploadStatus && (
              <div className={uploadStatus.includes('success') ? styles.success : styles.error}>
                {uploadStatus}
              </div>
            )}
          </section>
        )}

        {/* Content Moderation Section - Only for @pvpsiddhartha.ac.in */}
        {user?.email?.endsWith('@pvpsiddhartha.ac.in') && (
          <section className={styles.section}>
            <h2>Content Moderation</h2>
            <p className={styles.description}>
              Configure content filtering and moderation settings.
            </p>
            
            <div className={styles.formGroup}>
              <label htmlFor="deny_words">Blocked Words/Phrases</label>
              <textarea
                id="deny_words"
                value={formData.deny_words}
                onChange={(e) => setFormData({ ...formData, deny_words: e.target.value })}
                placeholder="Enter comma-separated words or phrases to block (e.g., spam, inappropriate, offensive)"
                className={styles.textarea}
                rows={4}
              />
              <small className={styles.hint}>
                Comma-separated list. Messages containing these words will be rejected.
              </small>
            </div>
          </section>
        )}

        {/* Model Parameters Section */}
        <section className={styles.section}>
          <h2>Model Parameters</h2>
          <p className={styles.description}>
            Fine-tune the AI model's behavior and response characteristics.
          </p>
          
          <div className={styles.formGroup}>
            <label htmlFor="max_tokens">Maximum Tokens</label>
            <input
              type="number"
              id="max_tokens"
              value={formData.max_tokens}
              onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
              min={100}
              max={4000}
              className={styles.input}
            />
            <small className={styles.hint}>
              Maximum length of generated responses (100-4000). Higher values allow longer responses.
            </small>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="temperature">Temperature</label>
            <div className={styles.temperatureControl}>
              <input
                type="range"
                id="temperature"
                value={parseFloat(formData.temperature)}
                onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                min={0}
                max={1}
                step={0.1}
                className={styles.slider}
              />
              <input
                type="number"
                value={formData.temperature}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  if (val >= 0 && val <= 1) {
                    setFormData({ ...formData, temperature: e.target.value });
                  }
                }}
                min={0}
                max={1}
                step={0.1}
                className={styles.numberInput}
              />
            </div>
            <small className={styles.hint}>
              Controls randomness (0-1). Lower values (0.3-0.5) = more focused and deterministic. 
              Higher values (0.7-1.0) = more creative and varied.
            </small>
          </div>
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
