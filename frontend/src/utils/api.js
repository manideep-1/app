import axios from 'axios';

// When running on localhost, always use local backend; otherwise use env
const isLocalhost = typeof window !== 'undefined' && window.location?.hostname === 'localhost';
const BACKEND_URL = isLocalhost ? 'http://localhost:8000' : (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000');
const API_BASE = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_BASE,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors (don't redirect if this was the /auth/me check on load — AuthProvider will set user null)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.config?.url?.includes('/auth/me')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return Promise.reject(error);
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    // 429: rate limit — caller can show error.response.data.detail
    return Promise.reject(error);
  }
);

export default api;
