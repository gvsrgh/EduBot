'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { apiClient } from './api';

interface AuthContextType {
  user: { email: string; username: string; is_admin: boolean } | null;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<{ email: string; username: string; is_admin: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = apiClient.getToken();
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.login({ email, password });
    apiClient.setToken(response.access_token);
    const userData = { 
      email: response.user.email, 
      username: response.user.username,
      is_admin: response.user.is_admin 
    };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    router.push('/chat');
  };

  const register = async (username: string, email: string, password: string) => {
    const response = await apiClient.register({ username, email, password });
    apiClient.setToken(response.access_token);
    const userData = { 
      email: response.user.email, 
      username: response.user.username,
      is_admin: response.user.is_admin 
    };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    router.push('/chat');
  };

  const logout = () => {
    apiClient.setToken(null);
    localStorage.removeItem('user');
    setUser(null);
    router.push('/chat');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
