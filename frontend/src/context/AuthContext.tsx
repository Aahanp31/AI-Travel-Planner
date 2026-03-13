'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '@/config/api';

interface User {
  id: number;
  email: string;
  username: string;
  profile_picture?: string;
  has_password?: boolean;
  trip_count: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, password: string) => Promise<void>;
  googleAuth: (googleToken: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const setAuthState = (access_token: string, userData: User) => {
    localStorage.setItem('auth_token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  };

  // Load token and user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }

    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(API_ENDPOINTS.login, {
        email,
        password
      });

      const { access_token, user: userData } = response.data;
      setAuthState(access_token, userData);
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  };

  const signup = async (email: string, username: string, password: string) => {
    try {
      const response = await axios.post(API_ENDPOINTS.signup, {
        email,
        username,
        password
      });

      const { access_token, user: userData } = response.data;
      setAuthState(access_token, userData);
    } catch (error: any) {
      console.error('Signup error:', error);
      throw new Error(error.response?.data?.error || 'Signup failed');
    }
  };

  const googleAuth = async (googleToken: string) => {
    try {
      const response = await axios.post(API_ENDPOINTS.googleAuth, {
        token: googleToken
      });

      const { access_token, user: userData } = response.data;
      setAuthState(access_token, userData);
    } catch (error: any) {
      console.error('Google auth error:', error);
      throw new Error(error.response?.data?.error || 'Google authentication failed');
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');

    // Clear state
    setToken(null);
    setUser(null);

    // Remove axios default header
    delete axios.defaults.headers.common['Authorization'];
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, googleAuth, logout, updateUser, isLoading }}>
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
