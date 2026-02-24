import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '@/utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser().catch(() => {});
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    await fetchUser();
    return response.data;
  };

  const register = async (email, username, password, full_name) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
      full_name,
    });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    await fetchUser();
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const sendSignupOtp = async (email) => {
    await api.post('/auth/send-signup-otp', { email });
  };

  const registerWithOtp = async (email, otp, username, password, full_name) => {
    const response = await api.post('/auth/verify-signup-otp', {
      email,
      otp,
      username,
      password,
      full_name,
    });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    await fetchUser();
    return response.data;
  };

  const loginWithGoogle = async (credential) => {
    const response = await api.post('/auth/google', { credential });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    await fetchUser();
    return response.data;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, sendSignupOtp, registerWithOtp, loginWithGoogle }}>
      {children}
    </AuthContext.Provider>
  );
};
