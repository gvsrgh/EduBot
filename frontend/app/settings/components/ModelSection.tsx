'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from '../settings.module.css';
import CustomSelect from '../../components/CustomSelect';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001/api';

interface ModelSectionProps {
  formData: {
    ai_provider: string;
  };
  setFormData: (data: any) => void;
  apiKeys: {
    openai_key: string;
    openai_model: string;
    gemini_key: string;
    gemini_model: string;
    ollama_url: string;
    ollama_model: string;
  };
  setApiKeys: (keys: any) => void;
}

export default function ModelSection({ 
  formData, 
  setFormData, 
  apiKeys, 
  setApiKeys 
}: ModelSectionProps) {
  const router = useRouter();
  
  const [ollamaTestStatus, setOllamaTestStatus] = useState('');
  const [testingOllama, setTestingOllama] = useState(false);
  
  const [openaiTestStatus, setOpenaiTestStatus] = useState('');
  const [testingOpenai, setTestingOpenai] = useState(false);
  
  const [geminiTestStatus, setGeminiTestStatus] = useState('');
  const [testingGemini, setTestingGemini] = useState(false);

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
      setTimeout(() => setOllamaTestStatus(''), 3000);
    }
  };
  
  const testOpenAIConnection = async () => {
    if (!apiKeys.openai_key) {
      setOpenaiTestStatus('✗ Please enter an OpenAI API key first');
      setTimeout(() => setOpenaiTestStatus(''), 3000);
      return;
    }
    
    setTestingOpenai(true);
    setOpenaiTestStatus('');
    
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
          setOpenaiTestStatus(`✓ ${result.message}. ${result.details || ''}`);
        } else {
          setOpenaiTestStatus(`✗ ${result.message}. ${result.details || ''}`);
        }
      } else {
        setOpenaiTestStatus('✗ Connection test failed');
      }
    } catch (err) {
      setOpenaiTestStatus('✗ Cannot connect to OpenAI');
    } finally {
      setTestingOpenai(false);
      setTimeout(() => setOpenaiTestStatus(''), 3000);
    }
  };
  
  const testGeminiConnection = async () => {
    if (!apiKeys.gemini_key) {
      setGeminiTestStatus('✗ Please enter a Gemini API key first');
      setTimeout(() => setGeminiTestStatus(''), 3000);
      return;
    }
    
    setTestingGemini(true);
    setGeminiTestStatus('');
    
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
          setGeminiTestStatus(`✓ ${result.message}. ${result.details || ''}`);
        } else {
          setGeminiTestStatus(`✗ ${result.message}. ${result.details || ''}`);
        }
      } else {
        setGeminiTestStatus('✗ Connection test failed');
      }
    } catch (err) {
      setGeminiTestStatus('✗ Cannot connect to Gemini');
    } finally {
      setTestingGemini(false);
      setTimeout(() => setGeminiTestStatus(''), 3000);
    }
  };

  return (
    <div className={styles.sectionContent}>
      <div className={styles.sectionIntro}>
        <h3>🤖 AI Configuration</h3>
        <p>Select your preferred AI provider and configure the model settings</p>
      </div>

      <div className={styles.privacyNotice}>
        <span className={styles.lockIcon}>🔒</span>
        <div>
          <strong>Privacy Notice:</strong> API keys are stored locally in your browser only. 
          We do NOT store your API keys on our servers.
        </div>
      </div>
    
      <div className={styles.formGroup}>
        <label htmlFor="ai_provider">Select Provider</label>
        <CustomSelect
          id="ai_provider"
          value={formData.ai_provider}
          onChange={(value) => setFormData({ ...formData, ai_provider: value })}
          options={[
            { value: 'ollama', label: 'Local Ollama (Recommended)' },
            { value: 'openai', label: 'OpenAI GPT-4' },
            { value: 'gemini', label: 'Google Gemini' },
            { value: 'auto', label: 'Auto (University-Provided API with Fallback)' },
          ]}
        />
      </div>
      
      {/* Ollama Configuration */}
      {formData.ai_provider === 'ollama' && (
        <div className={styles.providerConfig}>
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
        </div>
      )}
      
      {/* OpenAI Configuration */}
      {formData.ai_provider === 'openai' && (
        <div className={styles.providerConfig}>
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
            <CustomSelect
              id="openai_model"
              value={apiKeys.openai_model}
              onChange={(value) => {
                const newKeys = { ...apiKeys, openai_model: value };
                setApiKeys(newKeys);
                localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
              }}
              options={[
                { value: 'gpt-4o-mini', label: 'GPT-4o Mini (Recommended for Chatbots & QA)' },
              ]}
            />
            <small className={styles.hint}>
              Select the OpenAI model to use
            </small>
          </div>
          <div className={styles.formGroup}>
            <button
              type="button"
              onClick={testOpenAIConnection}
              disabled={testingOpenai || !apiKeys.openai_key}
              className={styles.testButton}
            >
              {testingOpenai ? 'Testing...' : '🔍 Test Connection'}
            </button>
            {openaiTestStatus && (
              <div className={openaiTestStatus.startsWith('✓') ? styles.testSuccess : styles.testError}>
                {openaiTestStatus}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Gemini Configuration */}
      {formData.ai_provider === 'gemini' && (
        <div className={styles.providerConfig}>
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
            <CustomSelect
              id="gemini_model"
              value={apiKeys.gemini_model}
              onChange={(value) => {
                const newKeys = { ...apiKeys, gemini_model: value };
                setApiKeys(newKeys);
                localStorage.setItem('edubot_api_keys', JSON.stringify(newKeys));
              }}
              options={[
                { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Recommended - Fast and efficient)' },
                { value: 'gemini-flash-latest', label: 'Gemini Flash Latest (Always latest flash model)' },
              ]}
            />
            <small className={styles.hint}>
              Select the Gemini model to use
            </small>
          </div>
          <div className={styles.formGroup}>
            <button
              type="button"
              onClick={testGeminiConnection}
              disabled={testingGemini || !apiKeys.gemini_key}
              className={styles.testButton}
            >
              {testingGemini ? 'Testing...' : '🔍 Test Connection'}
            </button>
            {geminiTestStatus && (
              <div className={geminiTestStatus.startsWith('✓') ? styles.testSuccess : styles.testError}>
                {geminiTestStatus}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
