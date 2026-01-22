import { AuthResponse, LoginRequest, RegisterRequest, MessageRequest, MessageResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    }
  }

  getToken() {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    // Add user's API keys from localStorage to headers (only if authenticated)
    if (typeof window !== 'undefined' && this.token) {
      const savedKeys = localStorage.getItem('edubot_api_keys');
      if (savedKeys) {
        try {
          const apiKeys = JSON.parse(savedKeys);
          if (apiKeys.openai_key) {
            headers['X-OpenAI-Key'] = apiKeys.openai_key;
          }
          if (apiKeys.openai_model) {
            headers['X-OpenAI-Model'] = apiKeys.openai_model;
          }
          if (apiKeys.gemini_key) {
            headers['X-Gemini-Key'] = apiKeys.gemini_key;
          }
          if (apiKeys.gemini_model) {
            headers['X-Gemini-Model'] = apiKeys.gemini_model;
          }
          if (apiKeys.ollama_url) {
            headers['X-Ollama-Url'] = apiKeys.ollama_url;
          }
          if (apiKeys.ollama_model) {
            headers['X-Ollama-Model'] = apiKeys.ollama_model;
          }
        } catch (e) {
          console.error('Failed to parse API keys from localStorage');
        }
      }
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async sendMessage(data: MessageRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();
